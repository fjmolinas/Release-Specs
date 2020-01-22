def print_results(results):
    packet_losses = [results[i][0] for i in range(len(results))]
    print("Summary of {packet losses, source pktbuf sanity, dest pktbuf sanity}:")
    for i in range(len(results)):
        print("Run {}: {} {} {}".format(i+1, packet_losses[i], results[i][1], results[i][2]))
    print("")
    print("Average packet losses: {}".format(sum(packet_losses)/len(packet_losses)))


def udp_send(source, dest, ip_dest, port, count, payload_size, delay):
    source.reboot()
    dest.reboot()

    dest.udp_server_start(port)
    source.udp_send(ip_dest, port, payload_size, count, delay)
    packet_loss = dest.udp_server_check_output(count, delay)
    dest.udp_server_stop()

    return packet_loss, source.is_empty(), dest.is_empty()
