# NetSage AI Network Troubleshooting Knowledge Base

## VLAN Troubleshooting

### Wrong Access VLAN

A host connected to an access port may lose connectivity when the switch port is assigned to the wrong VLAN.

Useful commands:

show vlan brief
show interfaces switchport
show interfaces <interface> switchport

Evidence to inspect:

- Access VLAN assigned to the interface
- Expected VLAN
- VLAN existence
- Port mode

Typical diagnosis:

The access interface is assigned to a VLAN different from the VLAN expected by the endpoint.

Recommended fix:

Assign the interface to the correct access VLAN.

Verification:

Confirm the interface VLAN assignment and test connectivity.

---

### Missing VLAN

A device cannot communicate with another device when the required VLAN does not exist on the switch.

Useful command:

show vlan brief

Evidence:

- Required VLAN
- Existing VLANs

Typical diagnosis:

The required VLAN is missing from the switch configuration.

Recommended fix:

Create the required VLAN and verify that the appropriate interfaces are assigned to it.

---

## Trunk Troubleshooting

### Missing VLAN on Trunk

A VLAN may exist on a switch but still fail between switches when the VLAN is not allowed on the trunk.

Useful commands:

show interfaces trunk
show interfaces <interface> switchport

Evidence:

- Trunk status
- Allowed VLAN list
- Native VLAN
- Required VLAN

Typical diagnosis:

The required VLAN is not allowed across the trunk.

Recommended fix:

Permit the required VLAN on the trunk.

Verification:

Confirm the VLAN appears in the trunk allowed VLAN list.

---

### Native VLAN Mismatch

A native VLAN mismatch occurs when two connected trunk interfaces use different native VLANs.

Useful command:

show interfaces trunk

Evidence:

- Native VLAN on each side
- Trunk state

Typical diagnosis:

The connected trunk interfaces use inconsistent native VLAN configuration.

Recommended fix:

Configure the same native VLAN on both sides.

---

## IP Addressing Troubleshooting

### Wrong Subnet Mask

A wrong subnet mask can prevent a host from determining whether a destination is local or remote.

Useful command:

ipconfig /all

or:

show ip interface brief

Evidence:

- Host IP address
- Subnet mask
- Default gateway

Typical diagnosis:

The host uses an incorrect subnet mask for its intended network.

Recommended fix:

Configure the correct subnet mask.

Verification:

Confirm the host network and gateway are correct and test connectivity.

---

### Interface IP Mismatch

Two directly connected router interfaces must use compatible addressing.

Useful command:

show ip interface brief

Evidence:

- Interface IP addresses
- Subnet masks
- Connected networks

Typical diagnosis:

The two interfaces are configured in incompatible IP networks.

Recommended fix:

Configure compatible IP addresses and subnet masks.

---

### Duplicate IP Address

Duplicate IP addressing occurs when multiple devices use the same IP address.

Useful commands:

show arp

ipconfig /all

Evidence:

- Repeated IP address
- Different MAC addresses

Typical diagnosis:

Multiple devices are using the same IP address.

Recommended fix:

Assign unique IP addresses.

Verification:

Clear stale ARP information if necessary and test connectivity.

---

## Default Gateway Troubleshooting

### Wrong Default Gateway

A host may communicate with local devices but fail to reach remote networks when its default gateway is incorrect.

Useful command:

ipconfig /all

Evidence:

- Host IP
- Subnet mask
- Default gateway

Typical diagnosis:

The configured gateway is incorrect or outside the host subnet.

Recommended fix:

Configure the correct gateway.

Verification:

Ping the gateway and then test a remote destination.

---

## Interface Troubleshooting

### Interface Administratively Down

An interface configured with shutdown will not forward traffic.

Useful command:

show interfaces status

show ip interface brief

Evidence:

administratively down

Typical diagnosis:

The interface is administratively disabled.

Recommended fix:

Use:

no shutdown

Verification:

Confirm the interface reaches an operational state.

---

### Interface Protocol Down

An interface may show physical link up while the line protocol remains down.

Useful command:

show interfaces

Evidence:

- Interface status
- Line protocol status
- Errors
- Duplex
- Speed

Typical diagnosis:

The physical or data-link connection has a problem.

Recommended checks:

- Cable
- Remote interface
- Encapsulation
- Speed
- Duplex
- Interface configuration

---

## Routing Troubleshooting

### Missing Route

A router cannot forward traffic to a destination network if there is no appropriate route.

Useful command:

show ip route

Evidence:

- Destination network
- Routing table
- Default route

Typical diagnosis:

The destination network is absent from the routing table.

Recommended fix:

Add a static route or correct the routing protocol configuration.

Verification:

Confirm the route appears in show ip route.

---

### Incorrect Static Route

A static route pointing to the wrong next hop can send packets toward an incorrect destination.

Useful command:

show ip route

Evidence:

- Destination network
- Next hop
- Exit interface

Typical diagnosis:

The static route points toward the wrong next hop or interface.

Recommended fix:

Correct the static route.

Verification:

Use show ip route and test the destination.

---

### Missing Default Route

A router without a default route may not know where to send traffic for unknown destinations.

Useful command:

show ip route

Typical diagnosis:

No suitable default route exists.

Recommended fix:

Configure the appropriate default route.

---

## OSPF Troubleshooting

### OSPF Neighbor Down

OSPF neighbors must establish an adjacency before exchanging routing information.

Useful command:

show ip ospf neighbor

Evidence:

- Neighbor state
- Router ID
- Interface
- Area

Typical diagnosis:

The OSPF adjacency has not reached FULL state.

Possible causes:

- Area mismatch
- Authentication mismatch
- Network mismatch
- Passive interface
- Hello/dead timer mismatch
- Interface problem

Recommended approach:

Check both sides of the adjacency.

---

### OSPF Area Mismatch

OSPF interfaces forming an adjacency must belong to compatible OSPF areas.

Useful commands:

show ip ospf interface
show ip ospf neighbor

Typical diagnosis:

The connected interfaces are configured for different OSPF areas.

Recommended fix:

Configure the correct matching OSPF area.

---

## DHCP Troubleshooting

### DHCP Pool Exhaustion

A DHCP server cannot allocate an address when the available pool has been exhausted.

Useful commands:

show ip dhcp pool
show ip dhcp binding

Typical diagnosis:

All usable addresses in the DHCP pool are allocated.

Recommended fix:

Expand the address pool or release unused leases.

---

### DHCP Wrong Network

A DHCP pool must match the network from which clients should receive addresses.

Useful configuration:

show running-config

Typical diagnosis:

The DHCP pool network does not correspond to the client VLAN subnet.

Recommended fix:

Correct the DHCP network and mask.

---

### DHCP Gateway Missing

Clients may receive an IP address but fail to reach remote networks when the DHCP pool does not provide a default gateway.

Typical diagnosis:

The DHCP pool lacks the correct default-router option.

Recommended fix:

Configure the correct default gateway in the DHCP pool.

---

### DHCP Relay Missing

Clients in one subnet cannot reach a DHCP server in another subnet without DHCP relay.

Useful command:

show running-config

Typical diagnosis:

The interface is missing the appropriate helper address.

Recommended fix:

Configure:

ip helper-address <DHCP-server>

Verification:

Renew the client DHCP lease.

---

## DNS Troubleshooting

### Incorrect DNS Server

A client can often reach an IP address but fail to resolve hostnames when its DNS server address is incorrect.

Useful command:

ipconfig /all

Typical diagnosis:

The client is configured with an incorrect DNS server.

Recommended fix:

Configure the correct DNS server.

---

### Missing DNS Record

A hostname cannot resolve when its required DNS record does not exist.

Typical diagnosis:

The requested hostname has no appropriate DNS record.

Recommended fix:

Create or correct the required DNS record.

---

### DNS Connectivity Failure

DNS resolution can fail when the client cannot reach the DNS server.

Useful checks:

ping <DNS-server>
nslookup <hostname>

Typical diagnosis:

The DNS server is unreachable.

Recommended fix:

Restore network connectivity between the client and DNS server.

---

## ACL Troubleshooting

### ACL Denies Traffic

An access control list can block otherwise valid traffic.

Useful commands:

show access-lists
show running-config

Evidence:

- ACL entries
- Permit/deny rules
- Interface
- Direction

Typical diagnosis:

A deny rule matches the required traffic.

Recommended fix:

Modify the ACL carefully to permit authorized traffic.

---

### ACL Applied to Wrong Interface

An ACL can cause unexpected results when applied to the wrong interface or direction.

Useful command:

show running-config

Typical diagnosis:

The ACL is attached to an unintended interface or direction.

Recommended fix:

Apply the ACL to the correct interface and direction.

---

### ACL Blocks DNS

DNS normally uses UDP port 53 and may also use TCP port 53.

Typical diagnosis:

The ACL blocks required DNS traffic.

Recommended fix:

Permit authorized DNS traffic.

---

### ACL Blocks SSH

SSH uses TCP port 22.

Typical diagnosis:

The ACL blocks authorized SSH management traffic.

Recommended fix:

Permit authorized TCP/22 traffic.

---

## NAT Troubleshooting

### NAT Not Translating

Inside hosts may fail to reach external networks when NAT is incorrectly configured.

Useful commands:

show ip nat translations
show ip nat statistics

Typical diagnosis:

Required NAT translation is not being created.

---

### NAT Inside Interface Missing

The internal interface must be identified as the NAT inside interface.

Useful configuration:

ip nat inside

Typical diagnosis:

The LAN interface lacks NAT inside configuration.

Recommended fix:

Configure the correct inside interface.

---

### NAT Outside Interface Missing

The external interface must be identified as the NAT outside interface.

Useful configuration:

ip nat outside

Typical diagnosis:

The WAN interface lacks NAT outside configuration.

Recommended fix:

Configure the correct outside interface.

---

### NAT ACL Incorrect

When NAT uses an ACL, the ACL must correctly match internal addresses.

Typical diagnosis:

The NAT ACL does not match the intended internal subnet.

Recommended fix:

Correct the ACL used by NAT.

---

## Wireless Troubleshooting

### Wrong SSID

A wireless client may connect to the wrong wireless network.

Typical diagnosis:

The client is attempting to connect to an incorrect SSID.

Recommended fix:

Select the intended SSID.

---

### Wireless Authentication Failure

A client may see an SSID but fail authentication.

Possible causes:

- Incorrect security key
- Incorrect authentication method
- Incorrect security configuration

Recommended fix:

Verify wireless security configuration and credentials.

---

### Wireless VLAN Mismatch

Wireless clients may connect successfully but be placed into the wrong VLAN.

Useful checks:

show vlan brief
show running-config

Typical diagnosis:

Wireless VLAN mapping does not match the intended client network.

Recommended fix:

Correct the wireless VLAN mapping.

---

### Wireless Gateway Issue

A wireless client may obtain an IP address but fail to reach remote networks when the gateway is incorrect.

Typical diagnosis:

The client has an incorrect default gateway.

Recommended fix:

Configure the correct gateway for the wireless client subnet.