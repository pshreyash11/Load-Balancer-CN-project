import multiprocessing
import os
import random
import socket
import sys
import signal
import time
import threading

from .log import logmsg, logerr
from .worker import LoadBalancerWorker
from .constants import DEFAULT_BUFFER_SIZE
from .config import LoadBalancerConfig  # Assuming config class is in another file


class LoadBalancerListener(multiprocessing.Process):
    '''
        Class that listens on a local port and forwards requests to workers
    '''

    def __init__(self, localAddr, localPort, workers, bufferSize=DEFAULT_BUFFER_SIZE):
        multiprocessing.Process.__init__(self)
        self.localAddr = localAddr
        self.localPort = localPort
        self.workers = workers
        self.bufferSize = bufferSize

        # Additional fields for weighted round robin
        self.weights = [worker['weight'] for worker in self.workers]
        self.total_weight = sum(self.weights)
        self.cumulative_weights = [sum(self.weights[:i+1]) for i in range(len(self.weights))]
        self.current_index = -1

        self.activeWorkers = []
        self.listenSocket = None
        self.cleanupThread = None
        self.keepGoing = True

    def cleanup(self):
        time.sleep(2)  # Wait for things to kick off
        while self.keepGoing is True:
            currentWorkers = self.activeWorkers[:]
            for worker in currentWorkers:
                worker.join(.02)
                if not worker.is_alive():  # Completed
                    self.activeWorkers.remove(worker)
            time.sleep(1.5)

    def closeWorkers(self, *args):
        self.keepGoing = False

        time.sleep(1)

        try:
            self.listenSocket.shutdown(socket.SHUT_RDWR)
        except:
            pass
        try:
            self.listenSocket.close()
        except:
            pass

        if not self.activeWorkers:
            if self.cleanupThread:
                self.cleanupThread.join(3)
            signal.signal(signal.SIGTERM, signal.SIG_DFL)
            sys.exit(0)

        for loadBalancerWorker in self.activeWorkers:
            try:
                loadBalancerWorker.terminate()
                os.kill(loadBalancerWorker.pid, signal.SIGTERM)
            except:
                pass

        time.sleep(1)

        remainingWorkers = []
        for loadBalancerWorker in self.activeWorkers:
            loadBalancerWorker.join(.03)
            if loadBalancerWorker.is_alive():  # Still running
                remainingWorkers.append(loadBalancerWorker)

        if remainingWorkers:
            time.sleep(1)
            for loadBalancerWorker in remainingWorkers:
                loadBalancerWorker.join(.2)

        if self.cleanupThread:
            self.cleanupThread.join(2)

        signal.signal(signal.SIGTERM, signal.SIG_DFL)
        sys.exit(0)

    def retryFailedWorkers(self, *args):
        '''
            retryFailedWorkers - Scans current workers for failed connections and retries with another worker.
        '''
        time.sleep(2)
        successfulRuns = 0
        while self.keepGoing is True:
            currentWorkers = self.activeWorkers[:]
            for worker in currentWorkers:
                if worker.failedToConnect.value == 1:
                    successfulRuns = -1  # Reset the "roll" of successful runs
                    logmsg('Found a failure to connect to worker\n')
                    numWorkers = len(self.workers)
                    if numWorkers > 1:
                        nextWorkerInfo = None
                        while (nextWorkerInfo is None) or (worker.workerAddr == nextWorkerInfo['addr'] and worker.workerPort == nextWorkerInfo['port']):
                            nextWorkerInfo = self.workers[random.randint(0, numWorkers - 1)]
                    else:
                        # No option but to try the same worker
                        nextWorkerInfo = self.workers[0]

                    logmsg('Retrying request from %s from %s:%d on %s:%d\n' % (
                        worker.clientAddr, worker.workerAddr, worker.workerPort, nextWorkerInfo['addr'], nextWorkerInfo['port']))

                    nextWorker = LoadBalancerWorker(worker.clientSocket, worker.clientAddr, nextWorkerInfo['addr'], nextWorkerInfo['port'], self.bufferSize)
                    nextWorker.start()
                    self.activeWorkers.append(nextWorker)
                    worker.failedToConnect.value = 0  # Reset failure flag
            successfulRuns += 1
            if successfulRuns > 1000000:
                successfulRuns = 6
            if successfulRuns > 5:
                time.sleep(2)
            else:
                time.sleep(.05)

    def run(self):
        signal.signal(signal.SIGTERM, self.closeWorkers)

        # Algorithm selection from config
        config = LoadBalancerConfig('setup.cfg')
        config.parse()
        selected_algorithm = config.getOptionValue('algorithm')

        while True:
            try:
                listenSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                listenSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                listenSocket.bind((self.localAddr, self.localPort))
                self.listenSocket = listenSocket
                break
            except Exception as e:
                logerr(f'Failed to bind to {self.localAddr}:{self.localPort}. "{str(e)}" Retrying in 5 seconds.\n')
                time.sleep(5)

        listenSocket.listen(5)

        # Start cleanup and retry threads
        self.cleanupThread = cleanupThread = threading.Thread(target=self.cleanup)
        cleanupThread.start()

        retryThread = threading.Thread(target=self.retryFailedWorkers)
        retryThread.start()

        # Select algorithm based on config
        if selected_algorithm == 'random':
            load_balancer_algorithm = self.random_algorithm
        elif selected_algorithm == 'round_robin':
            load_balancer_algorithm = self.round_robin
        elif selected_algorithm == 'weighted_round_robin':  # Add support for weighted round robin
            load_balancer_algorithm = self.weighted_round_robin

        try:
            while self.keepGoing is True:
                load_balancer_algorithm()

        except Exception as e:
            logerr(f'Got exception: {str(e)}, shutting down workers on {self.localAddr}:{self.localPort}\n')
            self.closeWorkers()
            return

        self.closeWorkers()


    def weighted_round_robin(self):
        try:
            (clientConnection, clientAddr) = self.listenSocket.accept()
        except Exception as e:
            logerr(f'Cannot bind to {self.localAddr}:{self.localPort}. Error: {e}\n')
            if self.keepGoing is True:
                time.sleep(3)
            return

        workerInfo = self.get_weighted_worker()  # Get weighted worker
        worker = LoadBalancerWorker(clientConnection, clientAddr, workerInfo['addr'], workerInfo['port'], self.bufferSize)
        self.activeWorkers.append(worker)
        worker.start()

        
    def get_weighted_worker(self):
        """Selects the next worker based on weights."""
        self.current_index = (self.current_index + 1) % self.total_weight
        for index, weight in enumerate(self.cumulative_weights):
            if self.current_index < weight:
                return self.workers[index]

    # Random selection algorithm
    def random_algorithm(self):
        try:
            (clientConnection, clientAddr) = self.listenSocket.accept()
        except Exception as e:
            logerr(f'Cannot bind to {self.localAddr}:{self.localPort}. Error: {e}\n')
            if self.keepGoing is True:
                time.sleep(3)
            return

        workerInfo = random.choice(self.workers)
        worker = LoadBalancerWorker(clientConnection, clientAddr, workerInfo['addr'], workerInfo['port'], self.bufferSize)
        self.activeWorkers.append(worker)
        worker.start()

    # Round-robin algorithm
    def round_robin(self):
        numWorkers = len(self.workers)
        currentIndex = 0
        while self.keepGoing is True:
            try:
                (clientConnection, clientAddr) = self.listenSocket.accept()
            except Exception as e:
                logerr(f'Cannot bind to {self.localAddr}:{self.localPort}. Error: {e}\n')
                if self.keepGoing is True:
                    time.sleep(3)
                continue

            workerInfo = self.workers[currentIndex]
            currentIndex = (currentIndex + 1) % numWorkers

            worker = LoadBalancerWorker(clientConnection, clientAddr, workerInfo['addr'], workerInfo['port'], self.bufferSize)
            self.activeWorkers.append(worker)
            worker.start()
