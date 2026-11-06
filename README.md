# OnePlus 6 (enchilada) — UniXNU device repository

A UniXNU format 2 device repository for the OnePlus 6 (A6003, 8 GB / 128 GB
SKU, SDM845 / "Napali"). It describes one board; the SDM845 SoC layer, the
UEFI firmware port and the kernel sources live in their own repositories.

**Status: skeleton. Nothing has been built or booted.** `feeds.toml` and
`board.toml [board] soc_source` are still placeholders because UniXNU has no
SDM845 SoC layer, so `unixnu defconfig` and `scripts/package.sh --check` stop
at the feed resolution step by design. See `AGENTS.md` for the rules that apply
inside this repository.

## Layout

| Path | Purpose |
| --- | --- |
| `board.toml` | Format 2 board record. Components, kernel, DTS source, firmware checkout, userdata window, boot image, payload and package sections. |
| `dts/enchilada.dts` | Self-contained board DTS. No `dtsi` include: there is no SoC layer to include from, so the DRAM range, GIC, PSCI, ARMv8 timer, UFS host/PHY and the TLMM window are written out in full. |
| `porting.toml` | Format 1 device record, one entry per required area. All areas are `planned`; the `inputs` of each carry the measured facts and mark their source. |
| `configs/enchilada_defconfig` | Kernel configuration for the console-only first boot: display, GPU, the native UFS driver and the owner Data mount are off. |
| `feeds.toml` | SoC source pin. Unresolved. |
| `patches/xnu/series` | Board patch list, in application order. Empty on purpose: no board patch has been ported and tested yet. |
| `scripts/package.sh` | Copy of the upstream `templates/package.sh`. Byte-identical, never edited. |
| `local.toml.example` | Where a local module checkout is declared. `local.toml` itself is ignored. |

## What was measured, and where it came from

Every hardware number in this repository has one of four sources, noted in a
comment next to it:

- **measured** on the target unit over `adb root` (partition table, LUN sizes,
  UFS controller and PHY windows, TLMM window, panel and touch wiring, DRAM
  extent, GIC and timer registers);
- **same-SoC port** (a format 1 community repository for this handset, corrected
  where it disagreed with the measurement — its userdata window belongs to the
  64 GB SKU, for instance);
- **Mu-Silicium source** (memory map, firmware FD base and size, the four edk2
  patches the firmware needs);
- **upstream documentation** (format 2 key names, the device tree binding table,
  the payload and boot image formats).

Three results worth knowing before reading the rest:

1. The SDM845 pin controller is one 12 MiB window at `0x03400000`. The firmware
   in use maps three 3 MiB windows starting at `0x03500000`, which leaves out the
   first MiB — the part that holds the control registers for GPIO 0 through 15.
   The board DTS therefore declares `0x03400000 + 0x00C00000` and nothing else.
2. The UFS host is `qcom,ufshc` at `0x01d84000 + 0x2500`, its PHY is
   `qcom,ufs-phy-qmp-v3` at `0x01d87000 + 0xda8`, and the inline crypto engine is
   at `0x01d90000 + 0x8000`. The DT node carries no `iommus` property, so claims
   about a UFS SMMU stream id have no device tree backing on this handset.
3. The apps SMMU is a `qcom,qsmmu-v500` controller (`0x15000000 + 0x80000`, TCU
   window at `0x150c2000`), not an MMU-500. XNU has no driver for that
   generation, which makes the memory area the largest known unknown.

## Bringing this up

Not possible yet. The order, once the SoC layer exists:

```sh
./unixnu defconfig enchilada_defconfig -D ../UniXNU-enchilada
./unixnu build firmware --uefi ../Mu-Silicium
./unixnu build payload --unique-chip-id <8 hex digits> --trust-cache <file> --data-ramdisk <seed>
./unixnu bootimg --uefi ../Mu-Silicium --dtb <path to the firmware dtb>
```

The host must be macOS or glibc Linux. Windows can run
`scripts/porting-record.py check` (which needs nothing but Python) and nothing
else.

## Hardware summary

| Item | Value |
| --- | --- |
| SoC | SDM845, 4x Cortex-A75 up to 2.80 GHz + 4x Cortex-A55 up to 1.77 GHz, no ARMv8.3 PAuth |
| DRAM | 8 GB LPDDR4X, described by the device tree as `0x80000000 + 0x100000000` and `0x180000000 + 0xFC8A0000` |
| Storage | 128 GB, six UFS LUNs, Samsung `KLUDG4U1EA-B0C1`, 4096-byte logical blocks |
| userdata | LBA 0x186f40 .. 0x1d06ffa at 4096 bytes = 110.00 GiB |
| Display | Samsung `sofef00` command-mode DSI panel, 1080x2280, two DSI controllers |
| Touch | Synaptics RMI over GENI I2C at `0xa90000`, address 0x20, IRQ 357 |
| Firmware | Mu-Silicium, FD at `0x9FC00000` size `0x300000` |
| OS profile | `ipados-17.7.11-21H461` (arm64 only) |

## Licence

BSD-2-Clause-Patent, as the rest of UniXNU.
