# Unitree_Go2_co-3dSlam_ATLAS
一个借助宇树机器人并基于ROS2环境下的FAST-LIO进行协同3Dslam建模的系统框架

## Go2 局域网连接与 VS Code 运行

如果你已经能在局域网 ping 通 Go2，但在 VS Code 里看不到机器人话题或控制不生效，可按下面流程执行。

### 1) 一键诊断连接

在工作区根目录运行：

```bash
./scripts/go2_doctor.sh --robot-ip 192.168.12.1 --domain 0 --rmw rmw_cyclonedds_cpp
```

该脚本会检查：
- 网络可达性（ping）
- ROS2 环境加载是否正常
- DDS 话题发现是否正常
- 是否能看到 Go2 关键话题（lf/sportmodestate, lf/lowstate）

### 2) 统一终端环境（手动方式）

```bash
source scripts/go2_env.sh 0 rmw_cyclonedds_cpp
ros2 topic list
```

重点参数：
- ROS_DOMAIN_ID：必须与机器人一致
- ROS_LOCALHOST_ONLY：脚本固定为 0，允许跨机器通信
- RMW_IMPLEMENTATION：与机器人侧保持一致（常用 CycloneDDS）

### 3) 启动业务节点（带环境包装）

```bash
./scripts/go2_run.sh --domain 0 --rmw rmw_cyclonedds_cpp -- ros2 launch go2_driver_py driver.launch.py use_rviz:=true
./scripts/go2_run.sh --domain 0 --rmw rmw_cyclonedds_cpp -- ros2 run go2_twist_bridge twist_bridge
./scripts/go2_run.sh --domain 0 --rmw rmw_cyclonedds_cpp -- ros2 run go2_teleop_ctrl_keyboard go2_teleop_crtl_keyboard
```

### 4) VS Code 任务面板运行

已提供任务文件：
- .vscode/tasks.json

可在 VS Code 的 Run Task 中直接运行：
- Go2: Doctor (LAN + DDS)
- Go2: Driver Launch (RViz)
- Go2: Twist Bridge
- Go2: Keyboard Teleop

### 5) 常见问题

- 能 ping 但看不到机器人话题：优先检查 ROS_DOMAIN_ID 和 RMW_IMPLEMENTATION 是否与机器人一致。
- 仍看不到话题：关闭 VPN，禁用虚拟网卡后重试。
- 环境丢失：每个新终端都要重新 source，或统一使用 scripts/go2_run.sh。

