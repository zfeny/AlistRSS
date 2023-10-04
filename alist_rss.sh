#!/bin/bash

while true; do
    echo "交互式命令面板"
    echo "1. 执行任务"
    echo "2. 停止任务"
    echo "3. 退出"
    read -p "请选择一个操作: " choice

    case "$choice" in
        1)
            # 执行任务
            echo "正在执行任务..."
            sleep 2  # 模拟任务执行
            ;;
        2)
            # 停止任务
            echo "正在停止任务..."
            sleep 2  # 模拟任务停止
            ;;
        3)
            # 退出
            echo "退出交互式命令面板"
            exit 0
            ;;
        *)
            echo "无效的选择，请重新选择."
            ;;
    esac
    read -p "按 Enter 继续..."
done
