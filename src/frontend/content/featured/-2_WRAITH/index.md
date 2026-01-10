---
date: '2026-01-01'
title: 'WRAITH'
cover: './wraith.png'
classified: true
tech:
  - Python
  - PostgreSQL
  - HTTP/REST
  - Virtual Machines
  - Debian/linux
  - systemd
  - PyAutoGUI
  - video streaming
  - Master/Slave Architecture
---

Built a distributed video downloader system coordinating 10+ concurrent VM scrapers with centralized VPN lease management, PostgreSQL job tracking, and fault-tolerant download pipelines (aria2, HLS/m3u8) - handling graceful shutdown, automatic retry logic, & cross-platform file synchronization to network storage