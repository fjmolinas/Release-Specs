from time import sleep


def ping(source, dest, ip_dest, count, payload_size, delay,
         channel=26, ping_timeout=10, empty_wait=3):
    # Reboot nodes before ping
    source.reboot()
    dest.reboot()

    # Set channel
    source.set_chan(source.get_first_iface(), channel)
    dest.set_chan(dest.get_first_iface(), channel)

    # Wait a little before starting to ping
    sleep(3)

    packet_loss = source.ping(count, ip_dest.split("/")[0], payload_size,
                              delay, ping_timeout)
    return packet_loss, source.is_empty(empty_wait), dest.is_empty(empty_wait)
