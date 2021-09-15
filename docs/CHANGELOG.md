<a name=""></a>
##  6.3 (2021-09-15)


#### Features

* **environments:**  add an interactive mode for container runs. ([c03738cd](https://github.com/polybench/benchbuild/commit/c03738cd90b9ea0ecc683b6c3785cfc6ce940f50))
* **log:**  add force_tty switch to control RichHandler. (#435) ([fe91f81c](https://github.com/polybench/benchbuild/commit/fe91f81c3199ca8f5361827a669ba4dc8123567b))
* **source:**  update git remote revisions. (#434) ([6899f2de](https://github.com/polybench/benchbuild/commit/6899f2de941e926760bbd2f7abce77d1aabb8f80))
* **utils/run:**  add unbuffered watch commands ([0b4bd04c](https://github.com/polybench/benchbuild/commit/0b4bd04c0f18c1f794620bff3319b95a6345a18a))

#### Bug Fixes

* **environments:**  pass format string to logging call (#427) ([bf52f27e](https://github.com/polybench/benchbuild/commit/bf52f27ee9b6a03b3599dd8538d2360776200c8c))
* **logging:**  make rich log to stderr by default (#415) ([7a59868e](https://github.com/polybench/benchbuild/commit/7a59868ec9f72fbd561dd6b246d3887687890c76), closes [#412](https://github.com/polybench/benchbuild/issues/412))
* **schema:**  silence SAWarning about caching (#428) ([f9d6ecab](https://github.com/polybench/benchbuild/commit/f9d6ecabf9b59a5a82d2de0032d6058e65cce9d9))
* **settings:**  BB_ENV is ignored when no config file is loaded" (#414) ([28d4c52f](https://github.com/polybench/benchbuild/commit/28d4c52f4409e5ad7a78b0edc117cb2c92e760d3))
* **sources:**  do not use protocol class as ABC ([2545684c](https://github.com/polybench/benchbuild/commit/2545684c6811e410b34957135fdb4b1402d58e11))



<a name=""></a>
##  6.2


#### Bug Fixes

*   use correct schema version ([beb9907e](https://github.com/polybench/benchbuild/commit/beb9907e291df020c39f0ca364fedfde669bb01b))
* **environments:**  notify the user, if image creation fails ([ab43787e](https://github.com/polybench/benchbuild/commit/ab43787e9f3cb1dd12b42469e9eabd1dcb721753))
* **project:**  do not track project classes twice ([4991ed99](https://github.com/polybench/benchbuild/commit/4991ed99015fe64ba347add1e1081ae884c47d4b), closes [#390](https://github.com/polybench/benchbuild/issues/390))
* **settings:**
  *  unbreak test cases. ([02745c46](https://github.com/polybench/benchbuild/commit/02745c46ce1a8d27d5f92b737b002c9fb9240e21))
  *  consistent settings behavior. ([25bfdd80](https://github.com/polybench/benchbuild/commit/25bfdd80e2ff4ab8e6fb85c2de75cf8b72c5b4b2))



<a name=""></a>
##  6.1


#### Bug Fixes

*   do not use global state to conffigure buildah/podman ([34d0aa26](https://github.com/polybench/benchbuild/commit/34d0aa266e55544c310c3387595553d8c8c3337e))
* **ci:**  typo. ([93ca8ee4](https://github.com/polybench/benchbuild/commit/93ca8ee4857a9dc65f909e7c5c81b6f6e1bf5dcb))
* **cli/project:**
  *  annotate print_layers ([8d3b1531](https://github.com/polybench/benchbuild/commit/8d3b1531fa8c521898a790e41ac63dc61c41e714))
  *  add neutral element for multiplication with reduce ([0bbf5664](https://github.com/polybench/benchbuild/commit/0bbf5664efb9dd1c20373b2c00f44c0f4f518630))
* **environments:**
  *  unshallow git clones before dissociating ([21aac7ce](https://github.com/polybench/benchbuild/commit/21aac7ce199b479b694c610a158650e605e583ea))
  *  remove left-over parameters ([6f3b2a8e](https://github.com/polybench/benchbuild/commit/6f3b2a8e057eee41fa33456e13b6d63da1dc5c5b))
  *  do not overwrite exported images. ([31da2ad7](https://github.com/polybench/benchbuild/commit/31da2ad7a31a4ebed7c8d02a8e261522a8e1a845), closes [#397](https://github.com/polybench/benchbuild/issues/397))
  *  remove optional image name argument from podman load ([c9bb2357](https://github.com/polybench/benchbuild/commit/c9bb2357a7f1b10c6ca9578a921c6a82f114746b), closes [#398](https://github.com/polybench/benchbuild/issues/398))
  *  reuse same status bar structure for all other cli subcommands ([256252f8](https://github.com/polybench/benchbuild/commit/256252f8daebc8ec51bd01b24d12873c320e746e))
  *  mypy warnings ([8f016d17](https://github.com/polybench/benchbuild/commit/8f016d17407d62e12b8d9258de4f3f172772e783))
  *  fix mypy/pylint annotations. ([379114c3](https://github.com/polybench/benchbuild/commit/379114c3b09812992a4043f7dd327ace3bfa7002))
  *  split return turple and baild out on error ([57d8e84c](https://github.com/polybench/benchbuild/commit/57d8e84c0b7245d8d73f97fb86314c9fd23d5731))
  *  mypy warnings ([b514cc56](https://github.com/polybench/benchbuild/commit/b514cc56e27b8250732cd3ce516256e993d16b16))
  *  add missing type conversion ([5211858c](https://github.com/polybench/benchbuild/commit/5211858c00b5c1d715148e8afce021c5f31907c2), closes [#388](https://github.com/polybench/benchbuild/issues/388))
  *  rework typing annotations for handlers ([100773ca](https://github.com/polybench/benchbuild/commit/100773ca2bac7d10e128149efd12a55a5876c2e9))
  *  fix linter/mypy warnings ([6d1b5e35](https://github.com/polybench/benchbuild/commit/6d1b5e35e9171d3079b6f86985fed4e6c8ba851b))
  *  make Add & Copy layers hashable ([2a38dced](https://github.com/polybench/benchbuild/commit/2a38dced58a8c4a658774aaabb7758ee762a2dc1))
  *  add missing sys import ([8ca2cb37](https://github.com/polybench/benchbuild/commit/8ca2cb37f10c71144f644bfd10202822e8b95203))
  *  import Protocol from typing_extensions, if python <= 3.8 ([5d3577a7](https://github.com/polybench/benchbuild/commit/5d3577a70e483c3f9940656fe0b266d6a5a1c364))
  *  handle 'None' for MaybeContainer return type ([1dc0aeef](https://github.com/polybench/benchbuild/commit/1dc0aeef0334570fecad6ac17d3ad7d08c770116))
  *  deal with multi-line container ids ([fdfd5342](https://github.com/polybench/benchbuild/commit/fdfd53422ce0fd4f7e8935c3ff37afaaabc0ba8f))
  *  do not spawn the FromLayer ([265c623e](https://github.com/polybench/benchbuild/commit/265c623ee707bfd5a2a76814bb9e620b78381125))
  *  explicitly state remote registry location ([84a591cc](https://github.com/polybench/benchbuild/commit/84a591cc80d76beaebb2b968bba03c75581ee46f))
* **project:**  project registration for groups ([6383d13e](https://github.com/polybench/benchbuild/commit/6383d13edd6cbd638b30dea6842b6fc480113b5e))
* **slurm:**
  *  fix pylint/mypy ([ddc06db9](https://github.com/polybench/benchbuild/commit/ddc06db941eecbe2b4c34a911fbd0712949eee65))
  *  do not modify slurm_node_dir ([be33d9a8](https://github.com/polybench/benchbuild/commit/be33d9a8bdd25f949ae7525d7cad88f6d6737743))
* **sources:**  unshallow only when needed ([6e0ae20c](https://github.com/polybench/benchbuild/commit/6e0ae20ce8fe3936d24368b66123e3bc3b1df131))
* **x264:**  use local name of source for lookup ([754718fc](https://github.com/polybench/benchbuild/commit/754718fc5f65d6197d8dadace620b0f19706f9bf), closes [#356](https://github.com/polybench/benchbuild/issues/356))

#### Features

*   tune down rich's custom log format ([04fbe347](https://github.com/polybench/benchbuild/commit/04fbe347cb3739893336d007e6376804576bc202))
*   add support for --export and --import flags in containers ([c18b7199](https://github.com/polybench/benchbuild/commit/c18b71991949efc79ea432828f23e29b999a687e))
* **cli/project:**
  *  add details view for a single project ([87c53e8d](https://github.com/polybench/benchbuild/commit/87c53e8d214eb47012546e0174f52c1350b61c36))
  *  change project view to a condensed format ([7af65f19](https://github.com/polybench/benchbuild/commit/7af65f194227f68b876ecd7f7f38b59e6edc4c0f))
* **environments:**
  *  just print env var name as error message ([b9044ef3](https://github.com/polybench/benchbuild/commit/b9044ef332a2d04df110b40b27e9c172c505a856))
  *  warn the user about too long paths for libpod ([325b5003](https://github.com/polybench/benchbuild/commit/325b5003dcb564e11153cb9ba01c2bf97493b5ff))
  *  enable debugging of failed image builds ([4c0e5ccd](https://github.com/polybench/benchbuild/commit/4c0e5ccd922c8061f0b58f1d74812ac5c1b03e74))
  *  provide more consistent output through rich ([3982228d](https://github.com/polybench/benchbuild/commit/3982228d2bbdb93a3130ce660e485c4f519e9563))
  *  add 'rmi' subcommand to delete images. ([80e239c6](https://github.com/polybench/benchbuild/commit/80e239c6663e628c6e14e1a09a73f7531d084041))
  *  make an error message stand out more clearly ([c5248f8a](https://github.com/polybench/benchbuild/commit/c5248f8a8584086973b7ea0c66d6bffc6221499f))
  *  add g++ to base image ([e20c572c](https://github.com/polybench/benchbuild/commit/e20c572cb7580e94d19776f476748fc8f494c45e))
  *  split image_exists into 2 implementations ([73d76d38](https://github.com/polybench/benchbuild/commit/73d76d38d63c5ac3792aee04c5454a83c82ac91c))
  *  split containers cli into 2 entitie ([6c3167d6](https://github.com/polybench/benchbuild/commit/6c3167d6f1a747e0e50638e3a9fd4204f23cea9e))
  *  add basic error handling to environments ([b711386e](https://github.com/polybench/benchbuild/commit/b711386ec0e31485d65e9c12c8dee68178e11dd9))
  *  emit layer creation events ([9a7fa149](https://github.com/polybench/benchbuild/commit/9a7fa1492e102f77c300a5487c03c7484ea26436))
  *  print layer construction progress ([404ac07e](https://github.com/polybench/benchbuild/commit/404ac07edbf408b41ec6282d40af5078dd36bd75))
  *  make layers hashable ([36432f02](https://github.com/polybench/benchbuild/commit/36432f02c7818ebefc18955bc2da4f85201845f5))
  *  step-wise image construction ([f5100ec8](https://github.com/polybench/benchbuild/commit/f5100ec8b5fa20047278bacb328b75cd39b05797))
  *  split Repositories and Unit of Work into 2 entities each ([6b9b9cd2](https://github.com/polybench/benchbuild/commit/6b9b9cd2be512facffa088faaa08e37e953ed989))
  *  add option to replace container images ([33cdac30](https://github.com/polybench/benchbuild/commit/33cdac30e752271614dd6c6363d61fa9a3534fe4), closes [#372](https://github.com/polybench/benchbuild/issues/372))
* **slurm:**  support variable number of subcommand arguments ([3df4cbd3](https://github.com/polybench/benchbuild/commit/3df4cbd3c7afbbe00a8c37f1391e2dfe60e4858e), closes [#396](https://github.com/polybench/benchbuild/issues/396))
* **utils/slurm:**  add customizable SLURM templates ([31022284](https://github.com/polybench/benchbuild/commit/31022284f2f492cb0f799309eb893b1a2b599b78))



<a name="6.0.1"></a>
### 6.0.1 (2020-12-29)


#### Bug Fixes

*   Avoid useless plugin spam when running with higher verbosity levels ([258bed40](https://github.com/polyjit/benchbuild/commit/258bed40dafea06b80c119b012515626d5763e99), closes [#354](https://github.com/polyjit/benchbuild/issues/354))
