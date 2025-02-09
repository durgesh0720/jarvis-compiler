FROM ubuntu:20.04

RUN apt update && apt install -y \
    curl git python3 python3-pip build-essential 

# Clone Piston
RUN git clone https://github.com/engineer-man/piston.git /piston

WORKDIR /piston

# Install dependencies
RUN ./scripts/setup.sh

EXPOSE 2000

CMD ["piston", "--isolated=/tmp/piston"]

