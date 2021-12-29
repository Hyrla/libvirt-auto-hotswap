hypervisor = "qemu"  # Valid options : "qemu", "xen", etc

vms = [
    {
        "domain": "win10-gauthier",
        "bus": [
            {
                "name": "USB Port front top left",
                "device_number": "003", 
                "bus_number": "002",
            },
            {
                "name": "USB Port front top right",
                "device_number": "003",
                "bus_number": "003",
            },
        ]
    }
]
