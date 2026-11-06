# Device repository: OnePlus 6 (enchilada / SDM845)

This repository is a UniXNU format 2 device repository. It owns the board
description and nothing else: see `docs/porting/device-repository.md` upstream.

## State

Nothing here has been built or booted. Every hardware value in `board.toml`,
`dts/enchilada.dts` and `configs/enchilada_defconfig` was measured on one
retail OnePlus 6 (A6003, 8 GB / 128 GB) with `adb root`, or read out of a
same-SoC community port and labelled as such in the comments. The two
placeholders that are still unresolved are `board.toml [board] soc_source` and
`feeds.toml` — the SDM845 SoC layer does not exist upstream, so this repository
cannot be fetched or configured yet.

## What is in here

| Path | Contents |
| --- | --- |
| `board.toml` | Format 2 board record: components, kernel, device tree, firmware, userdata window, boot image, payload, package |
| `porting.toml` | Format 1 device record: 13 required areas, all `planned` |
| `dts/enchilada.dts` | Self-contained board DTS (no dtsi; the SoC layer does not exist) |
| `configs/enchilada_defconfig` | Kernel configuration for a console-only first boot |
| `patches/xnu/series` | Board patch list — currently empty on purpose |
| `feeds.toml` | SoC source pin — unresolved, see above |
| `scripts/package.sh` | Byte-identical copy of the upstream template; never edit it |
| `.github/workflows/` | The two upstream reusable workflows |

## Rules for this repository

- `scripts/package.sh` is a copy of `templates/package.sh` in the UniXNU
  checkout. It is byte-identical and must stay that way. A board changes
  `board.toml`, never the script (`docs/porting/packaging.md:3-6`).
- Component IDs are catalog IDs from the UniXNU `components.toml`. Do not
  invent one: `scripts/porting-record.py` rejects unknown component names.
- `[components] include` and the areas of `porting.toml` have to agree. Every
  selected component needs an area that names it, or the record check fails with
  `components without an area`.
- Board patches live in `patches/xnu/series` and are read in file order. File
  names carry no order, and a directory of patches that is not listed here does
  nothing at all. This is the one difference from the format 1 community
  repositories that is easiest to get wrong.
- Every value added to `board.toml` gets a comment naming the source: `[LOCAL]`
  measured on this unit, `[PORT]` a same-SoC community port, `[MU]` Mu-Silicium
  source, or a document reference. A value with no source does not go in.
- The kernel command line has a 1000-byte ceiling and DarwinBoot copies it into a
 1024-byte buffer. `payload.kernel_args` is not set yet; when it is, count the
  bytes.
- Do not put the serial number, IMEI, or any per-unit identifier into this
  repository. The platform seed (`UNIXNU_UNIQUE_CHIP_ID`) is a CI secret.

## Build order (once the SoC layer exists)

```sh
# from the UniXNU checkout, with this repository as the device
./unixnu defconfig enchilada_defconfig -D ../UniXNU-enchilada
./unixnu build firmware --uefi ../Mu-Silicium
./unixnu build payload --unique-chip-id <8 hex digits> --trust-cache <file> --data-ramdisk <seed>
./unixnu bootimg --uefi ../Mu-Silicium --dtb <path to the firmware dtb>
```

Host requirement: macOS or glibc Linux. Windows is not supported by
`scripts/unixnu/cli.py` or by the Bash packaging path.
