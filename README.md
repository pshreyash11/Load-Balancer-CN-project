# 🚀 Load Balancer Project


Welcome to the **Load Balancer** project! This project is a multi-process TCP load balancer implemented in Python, supporting various algorithms such as **Round Robin**, **Random**, and **Weighted Round Robin**. It's designed to efficiently balance requests between multiple workers and can be configured through a simple configuration file.


## 📜 Table of Contents
- **Key Features**
- **Installation**
- **Usage**
- **Load Balancing Algorithms**
- **Contributors**

---

### 🎨 Key Features

- ⚡ **Multi-process**: Optimized using Python’s `multiprocessing` for handling multiple requests.
- 🎯 **Algorithm Support**: Choose from **Round Robin**, **Random**, or **Weighted Round Robin**.
- 📂 **Configurable**: Modify the behavior easily through an external configuration file.
- 🛠️ **Worker Management**: Dynamically manage workers based on their performance.
- 💾 **Efficient**: Uses buffered I/O for optimized socket communication.
- 🔧 **Proxy Management**: You can't directly send request to backend servers.

---


## 🔧 Installation

First, clone this repository:

```bash
git clone https://github.com/pshreyash11/Load-Balancer-CN-project.git
cd Load-balancer-CN-Project
```

## 🔧 Usage


1) now open new terminals and initiate servers

```bash
python runserver.py
```

this will open 4-5 terminals initiating different servers.


2) Setup setup.cfg file as per your needs
select sutaible algorithm and ports

```bash
python main.py setup.cfg
```


3) Open postman and send GET request to routes to test the code
e.g http://localhost:24003/main.py


## 📊 Load Balancing Algorithms

- The load balancer supports three algorithms:
   1) Round Robin: Distributes requests evenly among workers in sequence.
   2) Random: Assigns each incoming request to a random worker.
   3) Weighted Round Robin: Distributes requests based on worker weights, favoring more capable servers.

## 🤝 Contributors

Thanks to the following people for their contributions:

<a href="https://github.com/pshreyash11">
  <img src="https://avatars.githubusercontent.com/pshreyash11" alt="pshreyash11" width="50" height="50" style="border-radius: 50%;">
</a>

<a href="https://github.com/sahilpatil1804">
  <img src="https://avatars.githubusercontent.com/sahilpatil1804" alt="sahilpatil1804" width="50" height="50" style="border-radius: 50%;">
</a>

<a href="https://github.com/aapatil2004">
  <img src="https://avatars.githubusercontent.com/aapatil2004" alt="aapatil2004" width="50" height="50" style="border-radius: 50%;">
</a>

