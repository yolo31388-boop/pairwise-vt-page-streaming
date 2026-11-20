import math

# 页四元组统一为 (x, y, mip, layer)。
# feedback 采样比实际可见性晚一帧，因此任何一帧的驻留决策都必须同时
# 覆盖上一帧与当前帧的可见集，避免相机快速横移时边缘页反复换入换出。


def merge_visible_pages(previous, current):
    """合并前后两帧可见页并按四元组去重排序。

    保留首次出现顺序：上一帧的页在前，当前帧中新出现的页追加在后。
    """
    merged = []
    seen = set()
    for page in list(previous) + list(current):
        if page not in seen:
            seen.add(page)
            merged.append(page)
    return merged


def request_key(x, y, mip, layer):
    """生成含 mip 与 layer 的请求唯一键。

    键只含 (x, y) 会让不同 mip / layer 的换入请求互相覆盖，导致同一物理页
    被两个请求重复占用而引用计数只加一次；四元组键保证每个请求身份唯一，
    引用计数才能随请求原子地增减。
    """
    return f"{x}:{y}:{mip}:{layer}"


def table_index(x, y, table_width):
    """页表行主序索引。"""
    return y * table_width + x


def is_resident(page, table):
    """判断页是否已在页表。"""
    return page in table


def evict_candidates(entries, pinned, current_frame, max_age):
    """筛选可驱逐页，排除 pinned 与仍新鲜的页。

    entries 为 (page, last_used_frame) 序列。pinned 页正在被采样（含常驻的
    mip tail），绝不可驱逐；近 max_age 帧内采样过的页同样保留，防止刚用过
    的页仅因最久未用时间戳被换走。只有页龄严格大于 max_age 且未 pin 的页
    才返回，保持 entries 原顺序。
    """
    candidates = []
    for page, last_used in entries:
        if page in pinned:
            continue
        if current_frame - last_used <= max_age:
            continue
        candidates.append(page)
    return candidates


def pool_bucket_size(width, height, base):
    """按尺寸分级选择物理页桶。

    物理页池不再固定按 128×128 分配：取不小于 base 与页宽高最大值的最小
    2 的幂作为方形桶边长，非 2 的幂尺寸向上对齐后不会越界踩到相邻页。
    """
    needed = max(base, width, height)
    if needed <= 1:
        return 1
    return 1 << (needed - 1).bit_length()


def border_rect(x, y, width, height, border):
    """计算跨页采样的边界矩形。

    各向异性过滤会越过页边界取邻页纹素，上传时必须在四周复制 border 纹素
    的 page border，否则斜视角下页间接缝处出现细缝。返回外扩后的
    (x, y, width, height)。
    """
    return (
        x - border,
        y - border,
        width + 2 * border,
        height + 2 * border,
    )


def needs_fence(source_queue, target_queue):
    """跨队列传递页表是否需要 fence。

    间接绘制在 graphics 队列读取由 copy 队列写入的页表 buffer，队列不同
    时必须插 fence（页表双缓冲在该点切换），同队列内提交保序则无需 fence。
    """
    return source_queue != target_queue


def bc7_bytes(width, height):
    """BC7 压缩数据字节数。

    BC7 以 4×4 像素为一个压缩块、每块固定 16 字节，必须按块格式解码，
    不能按 RGBA8 逐像素解，否则通道错位。
    """
    blocks_x = (width + 3) // 4
    blocks_y = (height + 3) // 4
    return blocks_x * blocks_y * 16


def mip_tail_extent(width, height, mip_levels):
    """计算 mip tail 的末级尺寸。

    mip tail 常驻物理页池并在首个屏障前写入完毕，采样器永远不会读到尚未
    写入的 tail 而显示整块灰。末级尺寸逐级减半且不小于 1。
    """
    shift = mip_levels - 1
    return (max(1, width >> shift), max(1, height >> shift))


def clamp_layer(layer, layers):
    """钳制纹理数组层索引。

    mip 切换后层索引需重算并钳制到 [0, layers-1]，避免负值回绕到数组最后
    一层。
    """
    if layers <= 0:
        raise ValueError("layers must be positive")
    return max(0, min(layer, layers - 1))


def is_stale(request_frame, current_frame, max_lag):
    """判断请求是否过期。

    异步换入完成顺序可能错乱，完成时帧龄已严格超过 max_lag 的请求视为
    过期，其结果不得再占用物理页或改写页表。
    """
    return current_frame - request_frame > max_lag


def upload_priority(page):
    """页上传排序键，优先粗 mip。

    粗 mip（mip 索引小）先上传可让相机横移时先呈现低清全貌再逐块变清晰；
    同 mip 内按 layer、y、x 排序得到稳定的确定性顺序。
    """
    x, y, mip, layer = page
    return (mip, layer, y, x)


def page_budget(bytes_budget, page_bytes):
    """按字节预算计算页数量。"""
    if page_bytes <= 0:
        raise ValueError("page_bytes must be positive")
    return bytes_budget // page_bytes


def dedupe_requests(requests):
    """按页四元组去重且保留首次顺序。

    去重身份是完整的 (x, y, mip, layer)，不同 mip 或 layer 的同坐标页互不
    覆盖；同一四元组只保留首个请求，配合唯一键保证引用计数只累加一次。
    """
    deduped = []
    seen = set()
    for page in requests:
        if page not in seen:
            seen.add(page)
            deduped.append(page)
    return deduped
