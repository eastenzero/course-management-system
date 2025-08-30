import React, { useEffect, useRef, useCallback, useState } from 'react';
import { List, Spin } from 'antd';

export interface InfiniteListProps<T = any> {
  /** 数据源 */
  dataSource: T[];
  /** 渲染项函数 */
  renderItem: (item: T, index: number) => React.ReactNode;
  /** 加载更多函数 */
  loadMore: (page: number) => Promise<{ data: T[]; total: number; hasMore: boolean }>;
  /** 每页大小 */
  pageSize?: number;
  /** 是否有更多数据 */
  hasMore?: boolean;
  /** 加载状态 */
  loading?: boolean;
  /** 触发加载的距离 */
  threshold?: number;
  /** 列表高度 */
  height?: number | string;
  /** 空状态组件 */
  emptyComponent?: React.ReactNode;
  /** 加载组件 */
  loadingComponent?: React.ReactNode;
  /** 列表项样式 */
  itemStyle?: React.CSSProperties;
  /** 列表样式 */
  style?: React.CSSProperties;
  /** 列表类名 */
  className?: string;
  /** 网格配置 */
  grid?: {
    gutter?: number;
    column?: number;
    xs?: number;
    sm?: number;
    md?: number;
    lg?: number;
    xl?: number;
    xxl?: number;
  };
}

const InfiniteList = <T extends any>({
  dataSource,
  renderItem,
  loadMore,
  pageSize = 20,
  hasMore: externalHasMore,
  loading: externalLoading = false,
  threshold = 200,
  height = '100%',
  emptyComponent,
  loadingComponent,
  itemStyle,
  style,
  className,
  grid,
}: InfiniteListProps<T>) => {
  const [internalData, setInternalData] = useState<T[]>(dataSource);
  const [internalLoading, setInternalLoading] = useState(false);
  const listRef = useRef<HTMLDivElement>(null);
  const loadingRef = useRef(false);

  // 简化版无限滚动实现（暂时不使用useInfiniteScroll hook）
  const [currentPage, setCurrentPage] = useState(1);
  const [total, setTotal] = useState(0);
  const hookHasMore = currentPage * pageSize < total;
  const hookLoadMore = () => setCurrentPage(prev => prev + 1);

  const hasMore = externalHasMore !== undefined ? externalHasMore : hookHasMore;
  const loading = externalLoading || internalLoading;

  // 同步外部数据
  useEffect(() => {
    setInternalData(dataSource);
  }, [dataSource]);

  // 加载更多数据
  const handleLoadMore = useCallback(async () => {
    if (loading || !hasMore || loadingRef.current) return;

    loadingRef.current = true;
    setInternalLoading(true);

    try {
      const result = await loadMore(currentPage + 1);
      
      if (result) {
        setInternalData(prev => [...prev, ...result.data]);
        setTotal(result.total);
        hookLoadMore();
      }
    } catch (error) {
      console.error('加载更多数据失败:', error);
    } finally {
      setInternalLoading(false);
      loadingRef.current = false;
    }
  }, [loading, hasMore, currentPage, loadMore, setTotal, hookLoadMore]);

  // 滚动监听
  useEffect(() => {
    const container = listRef.current;
    if (!container) return;

    const handleScroll = () => {
      const { scrollTop, scrollHeight, clientHeight } = container;
      const distanceToBottom = scrollHeight - scrollTop - clientHeight;

      if (distanceToBottom <= threshold && hasMore && !loading) {
        handleLoadMore();
      }
    };

    container.addEventListener('scroll', handleScroll);
    return () => container.removeEventListener('scroll', handleScroll);
  }, [threshold, hasMore, loading, handleLoadMore]);

  // 渲染加载组件
  const renderLoading = () => {
    if (loadingComponent) {
      return loadingComponent;
    }

    return (
      <div style={{ textAlign: 'center', padding: '20px' }}>
        <Spin tip="加载中..." />
      </div>
    );
  };

  // 渲染空状态
  const renderEmpty = () => {
    if (emptyComponent) {
      return emptyComponent;
    }

    return (
      <div style={{ textAlign: 'center', padding: '40px', color: '#999' }}>
        暂无数据
      </div>
    );
  };

  return (
    <div
      ref={listRef}
      style={{
        height,
        overflow: 'auto',
        ...style,
      }}
      className={className}
    >
      {internalData.length === 0 && !loading ? (
        renderEmpty()
      ) : (
        <>
          <List
            dataSource={internalData}
            renderItem={(item, index) => (
              <List.Item style={itemStyle}>
                {renderItem(item, index)}
              </List.Item>
            )}
            grid={grid}
            split={false}
          />
          
          {loading && renderLoading()}
          
          {!hasMore && internalData.length > 0 && (
            <div style={{ textAlign: 'center', padding: '20px', color: '#999' }}>
              没有更多数据了
            </div>
          )}
        </>
      )}
    </div>
  );
};

export default React.memo(InfiniteList) as <T>(
  props: InfiniteListProps<T>
) => React.ReactElement;
