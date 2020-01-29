def print_results(results):
    packet_losses = [results[i][0] for i in range(len(results))]
    print("Summary of {packet losses, source pktbuf sanity, dest pktbuf sanity}:")
    for i in range(len(results)):
        print("Run {}: {} {} {}".format(i+1, packet_losses[i], results[i][1], results[i][2]))
    print("")
    print("Average packet losses: {}".format(sum(packet_losses)/len(packet_losses)))


def udp_send(src, dest, ip_dest, port, count, payload_size, delay):
    packet_loss = None
    src_pkt_buf_is_empty = None
    dest_pkt_buf_is_empty = None

    src.reboot()
    if dest is not None:
        dest.reboot()
        dest.udp_server_start(port)

    src.udp_send(ip_dest, port, payload_size, count, delay)
    if dest is not None:
        packet_loss = dest.udp_server_check_output(count, delay)
        dest.udp_server_stop()
        dest_pkt_buf_is_empty = src.is_empty()

    src_pkt_buf_is_empty = src.is_empty()

    return packet_loss, src_pkt_buf_is_empty, dest_pkt_buf_is_empty
