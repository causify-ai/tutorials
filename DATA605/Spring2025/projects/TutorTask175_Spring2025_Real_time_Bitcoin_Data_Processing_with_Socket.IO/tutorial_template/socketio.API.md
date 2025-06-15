# python-socketio API Reference

This markdown file explains how the `python-socketio` library works and how to use its core server-side features. This documentation is based on the official API: https://python-socketio.readthedocs.io/en/stable/api.html

## Overview

`python-socketio` provides a server-side interface for building WebSocket-based, real-time applications in Python.

We use `socketio.Server()` to define a WebSocket server and attach events using decorators.

---

## Key Components Demonstrated

### 1. `socketio.Server()`

Initializes the Socket.IO server object.

```python
sio = socketio.Server()
