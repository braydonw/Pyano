from IOPi import IOPi
import time


def main():
    """
    Main program function
    """
    bus = IOPi(0x21)

    bus.set_port_direction(0, 0x00)
    bus.write_port(0, 0x00)

    while True:
        for count in range(0, 255):
            bus.write_port(0, count)
            time.sleep(0.5)

        bus.write_port(0, 0x00)

if __name__ == "__main__":
    main()
    # test comment
