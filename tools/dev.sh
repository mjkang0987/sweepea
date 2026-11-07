#!/bin/bash
# usage: dev.sh [extra env...]  — 개발 서버를 (다시) 띄우고 준비될 때까지 기다림
cd /home/claude/sweepea
# Astro 7은 Node 22.23.4 이상. 작업 환경 node가 낮으면 Node 24를 tools/.node에 받아 쓴다(git 제외)
N=/home/claude/sweepea/tools/.node
if [ ! -x $N/package/bin/node ]; then mkdir -p $N && (cd $N && npm pack -q node-linux-x64@24 >/dev/null && tar xzf node-linux-x64-24*.tgz); fi
export PATH=$N/package/bin:$PATH
npx astro dev stop >/dev/null 2>&1
env SWEEPEA_BACKEND=mock "$@" npx astro dev --port 4321 >/dev/null 2>&1
for i in $(seq 1 30); do curl -s -o /dev/null -w "%{http_code}" localhost:4321/login | grep -q 200 && { echo up; exit 0; }; sleep 1; done; echo down; exit 1
