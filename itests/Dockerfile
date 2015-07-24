FROM ubuntu-debootstrap:14.04
RUN apt-get update && apt-get -y install sudo lsb-release

# Setup
ADD ./chronos-version /root/chronos-version
ADD ./install-chronos.sh /root/install-chronos.sh
RUN /root/install-chronos.sh

EXPOSE 4400 
ADD ./start-chronos.sh /root/start-chronos.sh
CMD /etc/init.d/zookeeper start && /root/start-chronos.sh
