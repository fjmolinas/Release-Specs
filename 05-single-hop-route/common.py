from time import sleep

PAYLOAD_SIZE = 1024
DELAY = 10


def print_results(results):
    packet_losses = [results[i][0] for i in range(len(results))]
    print("Summary of {packet losses, source pktbuf sanity, \
            dest pktbuf sanity}:")

    for i in range(len(results)):
        print("Run {}: {} {} {}".format(
            i+1, packet_losses[i], results[i][1], results[i][2]))

    print("")
    print("Average packet losses: {}".format(
        sum(packet_losses)/len(packet_losses)))


def single_hop_run(src, dest, ip_src, ip_dest, src_route, dest_route, rdv,
                   count, payload_size, delay=10, ping_timeout=10, empty_wait=3):
    src.reboot()
    dest.reboot()

    # give some time after reboot
    sleep(3)

    # get useful information
    src_ifc = src.get_first_iface()
    dest_ifc = dest.get_first_iface()
    ip_src_ll = dest.get_ip_addr()
    ip_dest_ll = src.get_ip_addr()

    # disable router advertisement
    if rdv is False:
        src.disable_rdv(src_ifc)
        dest.disable_rdv(dest_ifc)

    # add static IP addresses
    if ip_src:
        src.add_ip(src_ifc, ip_src)
    if ip_dest:
        dest.add_ip(dest_ifc, ip_dest)

    # sleep 1 second before sending data
    sleep(1)

    # add nib routes
    src.add_nib_route(src_ifc, src_route, ip_src_ll)
    dest.add_nib_route(dest_ifc, dest_route, ip_dest_ll)

    packet_loss = src.ping(count, ip_dest.split("/")[0], payload_size, delay, ping_timeout)

    return (packet_loss, src.is_empty(), dest.is_empty())
