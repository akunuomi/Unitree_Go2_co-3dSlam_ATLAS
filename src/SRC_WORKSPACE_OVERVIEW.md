# unitree_go2_ws/src 结构与功能总览

本文档用于快速理解当前 `src` 目录下的代码框架、包职责、数据流关系与启动建议。

## 1. 当前 src 目录框架（关键层级）

```text
src/
├── base/
│   ├── go2_description/
│   │   ├── launch/display.launch.py
│   │   ├── urdf/go2_description.urdf
│   │   ├── meshes/*.dae
│   │   └── package.xml
│   ├── go2_driver_py/
│   │   ├── go2_driver_py/driver.py
│   │   ├── launch/driver.launch.py
│   │   ├── params/driver.yaml
│   │   └── package.xml
│   ├── go2_twist_bridge/
│   │   ├── go2_twist_bridge/twist_bridge.py
│   │   ├── go2_twist_bridge/sport_model.py
│   │   └── package.xml
│   └── go2_teleop_ctrl_keyboard/
│       ├── go2_teleop_ctrl_keyboard/go2_teleop_crtl_keyboard.py
│       └── package.xml
│
├── helloworld/
│   └── helloworld_py/
│       ├── helloworld_py/hello.py
│       ├── helloworld_py/mynode.py
│       └── package.xml
│
├── tutorial/
│   ├── go2_tutorial_inter/
│   │   ├── action/Nav.action
│   │   ├── srv/Cruising.srv
│   │   ├── CMakeLists.txt
│   │   └── package.xml
│   └── go2_tutorial/
│       ├── go2_tutorial/go2_ctrl.py
│       ├── go2_tutorial/go2_state.py
│       ├── go2_tutorial/go2_cruising_service.py
│       ├── go2_tutorial/go2_cruising_client.py
│       ├── go2_tutorial/go2_nav_server.py
│       ├── go2_tutorial/go2_nav_client.py
│       ├── launch/go2_ctrl.launch.py
│       ├── launch/go2_state.launch.py
│       ├── launch/go2_cruising.launch.py
│       ├── launch/go2_nav.launch.py
│       ├── params/go2_state.yaml
│       ├── params/go2_cruising_service.yaml
│       └── package.xml
│
├── perception/
│   ├── FAST_LIO/
│   │   ├── src/laserMapping.cpp
│   │   ├── src/preprocess.cpp
│   │   ├── launch/mapping.launch.py
│   │   ├── config/*.yaml
│   │   └── package.xml
│   ├── go2_fastlio_adapter/   (当前为空目录)
│   └── go2_mapping_bringup/   (当前为空目录)
│
├── livox_ros_driver2/
│   ├── src/*.cpp
│   ├── launch_ROS2/*.py
│   ├── msg/CustomMsg.msg
│   ├── msg/CustomPoint.msg
│   └── package.xml
│
├── build/    (由 livox_ros_driver2 build.sh 在 src 下生成)
├── install/  (由 livox_ros_driver2 build.sh 在 src 下生成)
└── log/      (由 livox_ros_driver2 build.sh 在 src 下生成)
```

---

## 2. 各功能包作用说明

### 2.1 base 层（基础能力）

1. `go2_description`
- 作用：Go2 机器人模型描述与可视化资源。
- 提供：URDF、mesh、display 启动文件。
- 常见用途：在 RViz/TF 系统中可视化机器人模型。

2. `go2_driver_py`
- 作用：将 Unitree 原始状态话题转换为标准 ROS 接口。
- 关键功能：
  - 发布 `odom`
  - 广播里程计相关 TF
  - 发布 `joint_states`
- 价值：打通导航、状态监控、可视化的基础数据层。

3. `go2_twist_bridge`
- 作用：把 `cmd_vel`（Twist）桥接为 Unitree 控制请求 `/api/sport/request`。
- 价值：使上层通用 ROS 控制栈可驱动 Go2。

4. `go2_teleop_ctrl_keyboard`
- 作用：键盘遥控节点，直接发送运动控制请求。
- 价值：调试时不依赖额外上层控制器，快速验证底层动作链路。

### 2.2 tutorial 层（教学与业务示例）

1. `go2_tutorial_inter`
- 作用：接口定义包。
- 定义内容：
  - 服务：`Cruising.srv`
  - 动作：`Nav.action`
- 价值：统一教程中客户端/服务端的数据协议。

2. `go2_tutorial`
- 作用：教程业务逻辑包。
- 核心节点：
  - `go2_ctrl.py`：参数驱动控制
  - `go2_state.py`：里程计状态采样与打印
  - `go2_cruising_service.py` / `go2_cruising_client.py`：服务通信示例
  - `go2_nav_server.py` / `go2_nav_client.py`：动作导航示例
- 启动文件：封装了“驱动 + 教程节点”的组合启动。

### 2.3 perception 层（感知建图）

1. `FAST_LIO`
- 作用：激光-惯导里程计与建图（LIO）核心算法包。
- 依赖特点：对 `livox_ros_driver2` 和 Livox SDK2 有外部依赖。
- 常见用途：实时定位、地图构建。

2. `go2_fastlio_adapter`（空）
- 预期作用：Go2 数据到 FAST_LIO 输入格式的适配层。

3. `go2_mapping_bringup`（空）
- 预期作用：感知系统一键启动编排（driver + lio + rviz）。

### 2.4 传感器驱动层

1. `livox_ros_driver2`
- 作用：Livox 激光雷达 ROS2 驱动。
- 提供：
  - ROS2 launch
  - 自定义点云消息 `CustomMsg` / `CustomPoint`
- 与 FAST_LIO 关系：FAST_LIO 直接订阅该驱动输出的数据类型。

---

## 3. 当前工程的数据流（简化版）

```text
[键盘/导航/服务动作]
        |
        v
/api/sport/request  --->  Go2 机体执行
        ^
        |
cmd_vel -> go2_twist_bridge

Go2 状态话题(lf/sportmodestate, lf/lowstate)
        |
        v
go2_driver_py -> odom + joint_states + tf
        |
        +--> go2_tutorial(go2_state / cruising / nav)

livox_ros_driver2 -> 点云/自定义消息 -> FAST_LIO -> 位姿/地图
```

---

## 4. 编译与使用建议

1. 常规全量编译
```bash
cd /home/cyf/unitree_go2_ws
source /opt/ros/humble/setup.bash
colcon build
source install/setup.bash
```

2. 仅教程链路（不涉及感知）
```bash
colcon build --packages-skip fast_lio
```

3. 感知链路单独验证
```bash
colcon build --packages-select livox_ros_driver2 fast_lio
```

---

## 5. 维护建议

1. 建议将 `src/build`、`src/install`、`src/log` 迁回工作区根层的标准位置，避免与源码混放。
2. `perception/go2_fastlio_adapter` 与 `perception/go2_mapping_bringup` 可补齐为正式 ROS 包（package.xml + launch）。
3. 可在根目录补充一个统一总览文档（例如 `ARCHITECTURE.md`），并链接到本文件。

---

最后更新时间：2026-04-06
