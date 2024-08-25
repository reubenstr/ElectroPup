# lkm_m5

M5 stack library for Shanghai Lingkong technology products.

## Supported framework

* Arduino for ESP32

## Supported device (ESP32)

* M5Stack Basic V2.7

## Tested LKM motors

* [MF4015v2](http://en.lkmotor.cn/ProDetail.aspx?ProId=256)

## H/W Components

* [LKM products](https://www.mi.com/cyber-gear)
* [M5Stack Basic V2.7](https://shop.m5stack.com/collections/m5-controllers/products/esp32-basic-core-lot-development-kit-v2-7)
* [M5Stack Commu module \[M001\]](https://shop.m5stack.com/products/commu-module)
* [Grove Cable](https://www.seeedstudio.com/Grove-Universal-4-Pin-Buckled-20cm-Cable-5-PCs-pack.html)

## How to run sample

### Arduino IDE

1. Clone [MCP_CAN_LIB](https://github.com/coryjfowler/MCP_CAN_lib) and [lkm_m5](https://github.com/project-sternbergia/lkm_m5) to Arduino Library directory.

```bash
cd ~/Arduino/libraries
git clone https://github.com/coryjfowler/MCP_CAN_lib.git
git clone https://github.com/Locoduino/RingBuffer.git
git clone https://github.com/project-sternbergia/lkm_m5.git
```

2. Open [lkm_m5/examples/control_mode_example.ino](https://github.com/project-sternbergia/lkm_m5/blob/main/examples/control_mode_example.ino) with Arduino IDE


3. Build and write firmware to M5Stack

## Sample Code

### control_mode_example.ino

Check lkm motor behaviour using M5 stack.

* Middle Button - Change Control Mode (Position Mode -> Speed Mode -> Current Mode)
* Right Button  - Increase control value
* Left Button  - Decrease control value

## References

* [SHANGHAI LINGKONG TECHNOLOGY CO.,LTD Products](http://en.lkmotor.cn/Product.aspx)
* [SHANGHAI LINGKONG TECHNOLOGY CO.,LTD CAN PROTOCOL V2.35](http://en.lkmotor.cn/upload/20230706100134f.pdf)

## License

* MIT
