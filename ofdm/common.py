from time import sleep


def ping(source, dest, ip_dest, count, payload_size, delay, ping_timeout=10,
         empty_wait=3):
    sleep(3)
    packet_loss = source.ping(count, ip_dest.split("/")[0], payload_size,
                              delay, ping_timeout)
    return packet_loss, source.is_empty(empty_wait), dest.is_empty(empty_wait)
