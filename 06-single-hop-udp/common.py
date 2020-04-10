from time import sleep


def udp_send(src, dest, ip_dest, port, count, payload_size, delay,
             empty_wait=12):
    packet_loss = None
    src_pkt_buf_is_empty = None
    dest_pkt_buf_is_empty = None

    src.reboot()
    if dest is not None:
        dest.reboot()
        dest.udp_server_start(port)

    # Wait a little before sending udp messages
    sleep(3)

    src.udp_send(ip_dest, port, payload_size, count, delay)
    if dest is not None:
        packet_loss = dest.udp_server_check_output(count, delay)
        dest.udp_server_stop()
        dest_pkt_buf_is_empty = src.is_empty(timeout=empty_wait)

    src_pkt_buf_is_empty = src.is_empty(timeout=empty_wait)

    return packet_loss, src_pkt_buf_is_empty, dest_pkt_buf_is_empty
