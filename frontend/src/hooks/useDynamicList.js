import { useState, useRef, useLayoutEffect } from 'react';

/**
 * 动态列表加载 Hook
 * 实现了以下功能：
 * 1. 自动滚动：当在底部时，自动跟随新消息滚动。
 * 2. 性能优化：在底部时，仅渲染最新的 maxRenderCount 条记录。
 * 3. 历史加载：滚动到顶部时，自动加载 loadBatch 条历史记录。
 * 
 * @param {Array} fullList 完整的数据列表
 * @param {number} maxRenderCount 最大渲染数量（默认 200）
 * @param {number} loadBatch 每次加载的历史记录数量（默认 30）
 */
const useDynamicList = (fullList, maxRenderCount = 200, loadBatch = 30) => {
    const listRef = useRef(null);
    const [startIndex, setStartIndex] = useState(0);
    const [autoScroll, setAutoScroll] = useState(true);
    const scrollAdjustmentRef = useRef(null);
    
    // 计算有效的 startIndex
    // 如果在自动滚动模式下，强制使用计算出的最新起始位置，避免 useEffect 中的 setState 导致的额外渲染
    const effectiveStartIndex = autoScroll 
        ? Math.max(0, fullList.length - maxRenderCount) 
        : startIndex;

    // 渲染列表：从 effectiveStartIndex 开始的所有数据
    const renderList = fullList.slice(effectiveStartIndex);

    // 移除原有的 useEffect，因为 effectiveStartIndex 已经是派生状态
    // useEffect(() => { ... }, [fullList.length, autoScroll, maxRenderCount]);

    // 处理滚动位置恢复和自动滚动
    useLayoutEffect(() => {
        if (!listRef.current) return;

        if (scrollAdjustmentRef.current !== null) {
            // 恢复历史记录加载后的滚动位置
            const newScrollHeight = listRef.current.scrollHeight;
            const diff = newScrollHeight - scrollAdjustmentRef.current;
            if (diff > 0) {
                listRef.current.scrollTop = diff;
            }
            scrollAdjustmentRef.current = null;
        } else if (autoScroll) {
            // 自动滚动到底部
            listRef.current.scrollTop = listRef.current.scrollHeight;
        }
    }, [renderList, autoScroll]);

    // 滚动事件处理
    const handleScroll = () => {
        if (!listRef.current) return;
        
        const { scrollTop, scrollHeight, clientHeight } = listRef.current;
        
        // 1. 检测是否到达底部
        // 留出 10px 的缓冲区域
        const isBottom = scrollHeight - scrollTop - clientHeight < 10;
        
        if (isBottom) {
            if (!autoScroll) {
                setAutoScroll(true);
                // 进入自动滚动模式，effectiveStartIndex 会自动接管，无需手动 setStartIndex
            }
        } else {
            if (autoScroll) {
                // 离开自动滚动模式（用户向上滚动）
                // 此时必须将当前的有效起始位置同步回 state，
                // 否则 startIndex 可能还是旧值（例如 0），导致画面跳变
                setStartIndex(Math.max(0, fullList.length - maxRenderCount));
                setAutoScroll(false);
            }
        }

        // 2. 检测是否到达顶部（加载历史）
        // 使用 effectiveStartIndex 判断是否还有历史数据可加载
        if (scrollTop === 0 && effectiveStartIndex > 0) {
            // 记录当前滚动高度，用于 render 后恢复位置
            scrollAdjustmentRef.current = scrollHeight;
            
            // 向前加载 loadBatch 条
            const newStart = Math.max(0, effectiveStartIndex - loadBatch);
            setStartIndex(newStart);
        }
    };

    return {
        listRef,
        renderList,
        handleScroll,
        autoScroll
    };
};

export default useDynamicList;
