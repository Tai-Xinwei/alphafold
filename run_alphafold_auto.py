#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
批量跑 docker/run_docker.py：
- 传入一个根目录 root，遍历 root 下的每个子目录 <ID>/
- 对每个子目录，设置 --output_dir 为 <ID>/af2output
- 其它参数保持不变（按你给的命令）

用法：
  python run_af2_batch.py /path/to/root
可选：
  --docker_script  路径（默认：docker/run_docker.py）
  --dry-run        只打印命令不执行
  --only-exist     仅处理已存在的 af2output 目录
"""

import argparse
import subprocess
from pathlib import Path

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("root", help="根目录（包含多个子文件夹，每个子文件夹代表一个任务）")
    ap.add_argument("--docker_script", default="docker/run_docker.py",
                    help="docker/run_docker.py 的路径（默认：docker/run_docker.py）")
    ap.add_argument("--dry_run", action="store_true", help="只打印命令，不实际执行")
    ap.add_argument("--only_exist", action="store_true", help="仅处理已存在 af2output 的子目录")
    args = ap.parse_args()

    root = Path(args.root).resolve()
    if not root.is_dir():
        raise SystemExit(f"[错误] 根目录不存在或不是目录：{root}")

    # 固定参数（保持与你提供的命令一致）
    fixed = [
        "--fasta_paths=/project-abd/xinwei/msaprocess/casp15_easy/fasta",
        # "--fasta_paths=/project-abd/xinwei/msaprocess/casp_benchmark/fasta",
        "--max_template_date=2021-11-01",
        "--model_preset=monomer",
        "--data_dir=/project-abd/xinwei/msaprocess/af2data",
        "--use_precomputed_msas=true",
    ]

    docker_script = str(Path(args.docker_script).resolve())

    subdirs = [p for p in sorted(root.iterdir()) if p.is_dir()]
    if not subdirs:
        print(f"[提示] 根目录下没有子文件夹：{root}")
        return

    print(f"[信息] 将处理 {len(subdirs)} 个子目录\n")
    for d in subdirs:
        out_dir = d / "af2output"

        if args.only_exist and not out_dir.exists():
            print(f"[跳过] {d.name}: 未发现 {out_dir}")
            continue

        # 确保输出目录存在（如果不希望自动创建，可去掉 mkdir）
        out_dir.mkdir(parents=True, exist_ok=True)

        cmd = ["python3", docker_script, *fixed, f"--output_dir={out_dir}"]

        print("[命令]", " ".join(map(str, cmd)))
        if args.dry_run:
            continue

        # 执行
        try:
            subprocess.run(cmd, check=True)
            print(f"[完成] {d.name}\n")
        except subprocess.CalledProcessError as e:
            print(f"[失败] {d.name}（返回码 {e.returncode}），继续下一个。\n")

if __name__ == "__main__":
    main()
