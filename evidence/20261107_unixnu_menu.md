# Device evidence: the UniXNU menu on an enchilada

2026-11-07 22:22 UTC+8, ONEPLUS A6003 / enchilada / SDM845, serial 79ab****, slot a.

`fastboot boot` of a boot image packed from a RELEASE firmware (run 42380779873,
commit aaaff2d) put this on the screen:

```
UniXNU
version 0.1.0
built-in configuration

1  Return to firmware   action
2  Restart              action
3  Power off            action
4  Tools                action

Select an entry
Up/Down: select    Enter: boot
1-9: boot entry    Esc: stop timer
no boot entry found

drivers 0 loaded / 0 failed    kits 0
acpi 0
```

Image: boot.img 1,626,112 bytes, sha256
65728428603f7c718e1dce38e2ba0047436b0c99087bb7869b13f1a465e7c699, fd_sha256
5bd55aa882819b993ceeb25c0b285d2f78b090c0cb239f522a938205b76e8f7e, dtb_sha256
91b5ebf57d69fb2221e33c134754de6a932f70f2a1fba43bbac0ec45cee2d507,
header_version 1, shim_bytes 112, ramdisk_bytes 1.

"no boot entry found" and "drivers 0 loaded" are expected: the image carries a
one-byte placeholder ramdisk and no payload FAT volume, so UniXNU has no
EFI/UniXNU/unixnu.toml to read.

Why the earlier attempts stopped in DXE: the firmware had been built for the
DEBUG target, whose PE images exhaust the DXE page pool. A dispatcher probe
recorded "LoadImage failures = 14", every one of them Out of Resources
(VariableRuntimeDxe CBD2E4D5, EmbeddedMonotonicCounter FCABE6A7,
ResetSystemRuntimeDxe 4B28E4C7, RealTimeClock B336F62D, CapsuleRuntimeDxe
42857F0A and nine more GUIDs). Building RELEASE is the whole fix. The PcdDxe
depex patch stays because that deadlock was real, but the probe shows
LocateProtocol(gEfiPcdProtocol)=Success, so it was never what starved the
drivers.

Zero partition writes; slot a unchanged.

The XNU kernel was not started by this run, and no payload volume exists yet.
