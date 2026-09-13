# CHANGELOG

<!-- version list -->

## v1.4.2 (2026-09-13)

### Bug Fixes

- Gate Dependabot merges on required checks
  ([`c7f1263`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/c7f126363debc97409a8ddff797a0a6cb5472a9b))

- Identify Dependabot by pull request author
  ([#36](https://github.com/GethosTheWalrus/proxmox-mcp/pull/36),
  [`e8c1895`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/e8c189568d90ea6f4e47bdd6cbc2288b254937e8))

- Limit cluster tasks client-side ([#37](https://github.com/GethosTheWalrus/proxmox-mcp/pull/37),
  [`f806d3b`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/f806d3b9f97c286f6208d49f1a999be21f300c73))

- Tolerate MCP compatibility stub exports Push
  ([`3137e1f`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/3137e1f55d1121bf363ba8e4cffe2673107b000b))

- Upgrade container runtime packages ([#38](https://github.com/GethosTheWalrus/proxmox-mcp/pull/38),
  [`6731a9a`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/6731a9a2b99d15244defba4bb9105c9f69fc36a2))

### Build System

- **deps**: Bump actions/download-artifact from 4 to 8
  ([#28](https://github.com/GethosTheWalrus/proxmox-mcp/pull/28),
  [`4917129`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/4917129891967381a5c75382a8613d89a2192c1a))

- **deps**: Bump actions/github-script from 8 to 9
  ([#27](https://github.com/GethosTheWalrus/proxmox-mcp/pull/27),
  [`032f2bb`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/032f2bb86c0b4d6f0ce94d9433d8123303990790))

- **deps**: Bump actions/upload-artifact from 4 to 7
  ([#26](https://github.com/GethosTheWalrus/proxmox-mcp/pull/26),
  [`2365ef2`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/2365ef295c18f801bd656156266eefbf52c816f5))

- **deps**: Bump google/osv-scanner-action/.github/workflows/osv-scanner-reusable-pr.yml
  ([#32](https://github.com/GethosTheWalrus/proxmox-mcp/pull/32),
  [`122e792`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/122e792456f50aa73d282062cea70114b1607d0f))

- **deps**: Bump google/osv-scanner-action/.github/workflows/osv-scanner-reusable.yml
  ([#33](https://github.com/GethosTheWalrus/proxmox-mcp/pull/33),
  [`0801594`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/0801594228cbcc9082fa06cd95497f8f4688036b))

- **deps**: Bump google/osv-scanner-action/.github/workflows/osv-scanner-reusable.yml
  ([#29](https://github.com/GethosTheWalrus/proxmox-mcp/pull/29),
  [`c755d4e`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/c755d4e6fe94ddee09335fdfcbd9dd5a2e9d96f7))

### Continuous Integration

- Harden release workflow ([#39](https://github.com/GethosTheWalrus/proxmox-mcp/pull/39),
  [`010f9be`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/010f9bef3b5ac2b59a707b608291b9ecee0de48a))

- Use release app token ([#39](https://github.com/GethosTheWalrus/proxmox-mcp/pull/39),
  [`010f9be`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/010f9bef3b5ac2b59a707b608291b9ecee0de48a))

### Documentation

- Remove stale changelog ([#25](https://github.com/GethosTheWalrus/proxmox-mcp/pull/25),
  [`4dd32f2`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/4dd32f2b59ee5023e013b0defa3a5c41532ae1e2))

### Testing

- Clean up lint issues ([#24](https://github.com/GethosTheWalrus/proxmox-mcp/pull/24),
  [`f1ae811`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/f1ae811b7ce37ed7055778465ed5410342915600))


## v1.4.1 (2026-07-30)

### Bug Fixes

- Remove semicolons from tool descriptions
  ([#23](https://github.com/GethosTheWalrus/proxmox-mcp/pull/23),
  [`5c4d343`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/5c4d343ea6e688e99b31972455c5bc87b623f0ee))


## v1.4.0 (2026-07-30)

### Bug Fixes

- Address ghas review comments ([#22](https://github.com/GethosTheWalrus/proxmox-mcp/pull/22),
  [`06cd9ff`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/06cd9ff18e7d374d0842070dfb75871384c94122))

- Stabilize manifest and semgrep scan
  ([#22](https://github.com/GethosTheWalrus/proxmox-mcp/pull/22),
  [`06cd9ff`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/06cd9ff18e7d374d0842070dfb75871384c94122))

### Build System

- **deps**: Bump actions/checkout from 6 to 7
  ([#14](https://github.com/GethosTheWalrus/proxmox-mcp/pull/14),
  [`16c07b7`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/16c07b76cfbdefc6e3995192d7ccb9be7647a4ab))

- **deps**: Bump actions/setup-python from 6 to 7
  ([#19](https://github.com/GethosTheWalrus/proxmox-mcp/pull/19),
  [`9f25037`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/9f25037e6de184e81555f792a2138e3da0812f94))

- **deps-dev**: Update black requirement from >=25.0.0 to >=26.3.1
  ([#3](https://github.com/GethosTheWalrus/proxmox-mcp/pull/3),
  [`b90b891`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/b90b8915e27006a4eafb394cf56664c28f8ee991))

- **deps-dev**: Update black requirement from >=26.3.1 to >=26.5.0
  ([#9](https://github.com/GethosTheWalrus/proxmox-mcp/pull/9),
  [`fcbc7ff`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/fcbc7ff378cada1c354a89fb78064183eb6ac175))

- **deps-dev**: Update black requirement from >=26.5.0 to >=26.5.1
  ([#11](https://github.com/GethosTheWalrus/proxmox-mcp/pull/11),
  [`ad43013`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/ad4301397db8f0b051836e8bcea7800f47d5a39e))

- **deps-dev**: Update flake8 requirement from >=6.0.0 to >=7.3.0
  ([#6](https://github.com/GethosTheWalrus/proxmox-mcp/pull/6),
  [`8190536`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/819053645186e25fc19f754474e8d3acb1cfb796))

- **deps-dev**: Update mypy requirement from >=1.0.0 to >=1.20.2
  ([#2](https://github.com/GethosTheWalrus/proxmox-mcp/pull/2),
  [`9a6f3bc`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/9a6f3bc06688d1fd2d251e2c567e628d9563fca8))

- **deps-dev**: Update mypy requirement from >=1.20.2 to >=2.0.0
  ([#8](https://github.com/GethosTheWalrus/proxmox-mcp/pull/8),
  [`da917bc`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/da917bc650f5e5ca3a25510c3d5741074ffbcc49))

- **deps-dev**: Update mypy requirement from >=2.0.0 to >=2.1.0
  ([#10](https://github.com/GethosTheWalrus/proxmox-mcp/pull/10),
  [`d42df2e`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/d42df2e80b9fa479a0936d4c6ad555ff4bb5c30c))

- **deps-dev**: Update mypy requirement from >=2.1.0 to >=2.2.0
  ([#16](https://github.com/GethosTheWalrus/proxmox-mcp/pull/16),
  [`a38b3f7`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/a38b3f790a818d6c70ca47307ffd66ea104a0a34))

- **deps-dev**: Update mypy requirement from >=2.2.0 to >=2.3.0
  ([#18](https://github.com/GethosTheWalrus/proxmox-mcp/pull/18),
  [`647fff6`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/647fff67e647522247247bdd5c7fc7d707bab913))

- **deps-dev**: Update pre-commit requirement from >=4.0.0 to >=4.6.0
  ([#4](https://github.com/GethosTheWalrus/proxmox-mcp/pull/4),
  [`35ef00c`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/35ef00c833368a7440e264840bd136dd9acb6e15))

- **deps-dev**: Update pre-commit requirement from >=4.6.0 to >=4.6.1
  ([#20](https://github.com/GethosTheWalrus/proxmox-mcp/pull/20),
  [`9a5bf48`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/9a5bf48fd58f5c905f8a33609875fcfaaa7a7778))

- **deps-dev**: Update pytest requirement from >=7.0.0 to >=9.0.3
  ([#7](https://github.com/GethosTheWalrus/proxmox-mcp/pull/7),
  [`1e0fa68`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/1e0fa684f76453856b05e14b3f0afbb38afaab06))

- **deps-dev**: Update pytest requirement from >=9.0.3 to >=9.1.0
  ([#13](https://github.com/GethosTheWalrus/proxmox-mcp/pull/13),
  [`c569b2e`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/c569b2eaa53b783b1c3e863a11451fd8f9716256))

- **deps-dev**: Update pytest requirement from >=9.1.0 to >=9.1.1
  ([#15](https://github.com/GethosTheWalrus/proxmox-mcp/pull/15),
  [`060b7f5`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/060b7f5bbbf14bb69f1dac928f1566125e0b03b5))

- **deps-dev**: Update pytest-asyncio requirement
  ([#12](https://github.com/GethosTheWalrus/proxmox-mcp/pull/12),
  [`16145d7`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/16145d74b15cd88f83d29886fc3f4e27fa5ce46a))

- **deps-dev**: Update pytest-asyncio requirement
  ([#5](https://github.com/GethosTheWalrus/proxmox-mcp/pull/5),
  [`5072293`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/507229325267bb9125471a15261e45a163d143cd))

### Features

- Add lazy tool routing and security workflows
  ([#22](https://github.com/GethosTheWalrus/proxmox-mcp/pull/22),
  [`06cd9ff`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/06cd9ff18e7d374d0842070dfb75871384c94122))


## v1.3.0 (2026-03-26)

### Bug Fixes

- Resolve lint, type check, and security scan CI failures
  ([`1551fe2`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/1551fe2423a878310b28ed67f4a882739a4bfca0))

### Documentation

- Add TOOL_ROUTING to README configuration table
  ([`6ec7b95`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/6ec7b952c69450070a6f27f98fe378457d350c69))

### Features

- Conditionally register routing tools only when TOOL_ROUTING is enabled
  ([`197be14`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/197be14916963778da50dd24bc47d77b81ffcdf2))


## v1.2.0 (2026-03-23)

### Features

- Add configurable PROXMOX_TIMEOUT env var (default 30s)
  ([`904b6cd`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/904b6cd28524c64c5f9269b31a456b3983ece012))


## v1.1.1 (2026-03-23)

### Bug Fixes

- Pass limit param in get_cluster_tasks and use hyphens in update_cluster_options
  ([`8adc4ea`](https://github.com/GethosTheWalrus/proxmox-mcp/commit/8adc4ea8789f27c2468d4787054e670a71635964))


## v1.1.0 (2026-03-23)


## v1.0.0 (2026-03-23)

- Initial Release
