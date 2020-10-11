# script for testing water level reading
# generates a self calibrated percentage of fullness.
#
# bar chart ref - https://alexwlchan.net/2018/05/ascii-bar-charts/

import machine
import time

# define pins
CAP_PIN = const(14)

# define starting values
min_value = 500
max_value = 800

bar_size = 25

# setup inputs and outpus
t = machine.TouchPad(machine.Pin(CAP_PIN))

# main
def run():
    print("** Water Level Test **")
    try:
        print("press ctrl-c to stop")
        print("")

        while True:
            value = t.read()

            # adjust if new min/max value
            min_value = min(min_value, t)
            max_value = max(max_value, t)

            percentage = (max_value - value)/(max_value - min_value)

            # The ASCII block elements come in chunks of 8, so we work out how
            # many fractions of 8 we need.
            bar_chunks, remainder = divmod(int(percentage * bar_size * 8), 8)

            # draw full width chunks
            bar = '█' * bar_chunks

            # add chunk fraction
            if remainder > 0:
                bar += chr(ord('█') + (8 - remainder))

            print("Water level: {0:>5.1f}% |{1:<25s}".format(percentage*100, bar))
            print("                    |{0:<25s}".format(bar))
            print("min value: {0:<6d} max value: {1:<6d} raw value: {2:<6d}".format(min_value, max_value, value))
            print('\033[A'*4)

            time.sleep(.5)
        
    except  KeyboardInterrupt:
        print("Program stopped by user")
    except:
        print("Something went wrong")
    finally:
        print("Goodbye")

if __name__ == '__main__':
    run()