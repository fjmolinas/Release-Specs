
import time

def print_results(results):
    packet_losses = [results[i][0] for i in range(len(results))]
    print("Summary of {packet losses, source pktbuf sanity, dest pktbuf sanity}:")
    for i in range(len(results)):
        print("Run {}: {} {} {}".format(i+1, packet_losses[i], results[i][1], results[i][2]))
    print("")
    print("Average packet losses: {}".format(sum(packet_losses)/len(packet_losses)))


def ping(source, dest, ip_dest, count, payload_size, delay, ping_timeout=10, empty_wait=3):
    source.reboot()
    dest.reboot()

    # give some time after reboot
    time.sleep(3)

    packet_loss = source.ping(count, ip_dest.split("/")[0], payload_size, delay, ping_timeout)
    return packet_loss, source.is_empty(empty_wait), dest.is_empty(empty_wait)
