import math

def merge_visible_pages(previous, current):
    """合并前后两帧可见页并按四元组去重排序。"""
    raise NotImplementedError("TODO: merge_visible_pages")

def request_key(x, y, mip, layer):
    """生成含 mip 与 layer 的请求唯一键。"""
    raise NotImplementedError("TODO: request_key")

def table_index(x, y, table_width):
    """页表行主序索引。"""
    raise NotImplementedError("TODO: table_index")

def is_resident(page, table):
    """判断页是否已在页表。"""
    raise NotImplementedError("TODO: is_resident")

def evict_candidates(entries, pinned, current_frame, max_age):
    """筛选可驱逐页，排除 pinned 与仍新鲜的页。"""
    raise NotImplementedError("TODO: evict_candidates")

def pool_bucket_size(width, height, base):
    """按尺寸分级选择物理页桶。"""
    raise NotImplementedError("TODO: pool_bucket_size")

def border_rect(x, y, width, height, border):
    """计算跨页采样的边界矩形。"""
    raise NotImplementedError("TODO: border_rect")

def needs_fence(source_queue, target_queue):
    """跨队列传递页表是否需要 fence。"""
    raise NotImplementedError("TODO: needs_fence")

def bc7_bytes(width, height):
    """BC7 压缩数据字节数。"""
    raise NotImplementedError("TODO: bc7_bytes")

def mip_tail_extent(width, height, mip_levels):
    """计算 mip tail 的末级尺寸。"""
    raise NotImplementedError("TODO: mip_tail_extent")

def clamp_layer(layer, layers):
    """钳制纹理数组层索引。"""
    raise NotImplementedError("TODO: clamp_layer")

def is_stale(request_frame, current_frame, max_lag):
    """判断请求是否过期。"""
    raise NotImplementedError("TODO: is_stale")

def upload_priority(page):
    """页上传排序键，优先粗 mip。"""
    raise NotImplementedError("TODO: upload_priority")

def page_budget(bytes_budget, page_bytes):
    """按字节预算计算页数量。"""
    raise NotImplementedError("TODO: page_budget")

def dedupe_requests(requests):
    """按页四元组去重且保留首次顺序。"""
    raise NotImplementedError("TODO: dedupe_requests")
