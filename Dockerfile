FROM cornerskyless/noilinux:latest
LABEL CornerSkyless 573196853@qq.com

RUN apt install -y libc6-dev

RUN useradd --create-home --no-log-init --shell /bin/bash judger
COPY core /root/Judge-Core
RUN mkdir /root/judge_file
RUN mkdir /home/judger/run_env
RUN chown judger:judger /home/judger/run_env
WORKDIR /root/Judge-Core
CMD ["bash"]