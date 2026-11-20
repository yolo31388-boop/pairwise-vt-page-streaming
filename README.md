# pairwise-vt-page-streaming

虚拟纹理在相机快速横移时整片地表先糊成低清再逐块变清晰，feedback 采到的可见页比实际晚一帧，边缘页在页表里反复换入换出；页表项更新和采样之间没有屏障，mip tail 尚未写入就被采到，出现整块灰；异步换入完成顺序错乱，同一物理页被两个请求重复占用，引用计数只加了一次；驱逐只按最久未用时间戳，没排除正在采样的 pinned 页，刚用过的页被换走；物理页池按固定 128×128 分配，非 2 的幂尺寸越界踩到相邻页；各向异性采样跨页边界未复制 page border，斜视角出现细缝；间接绘制读的页表 buffer 在 copy 与 graphics 队列之间没有 fence，偶发读到旧表；BC7 压缩页在 CPU 端按 RGBA8 解，通道错位；纹理数组层索引在 mip 切换后未重算，负值回绕到最后一层；请求去重键只含 (x,y)，不同 mip 与 layer 互相覆盖。render/virtual_texture.py 是核心，tests/test_virtual_texture.py 15个红。要修的是：合并前后两帧可见集；页表双缓冲并插屏障；换入任务用唯一键并原子维护引用计数；驱逐排除 pinned 与近 N 帧采样页；页池按尺寸分级；跨页采样复制边界；copy 到 graphics 加 fence；按块格式解码；层索引钳制；去重键包含 mip 与 layer；mip tail 常驻。

## 运行

```bash
python -m pytest tests -q
```

初始状态：15 个用例失败。修复实现使全部用例通过，不要修改 `tests/` 下的测试。

子方向：图形渲染；任务类型：Bugfix；语言/框架：Python 3, pytest；环境可复现等级：无外部依赖。
