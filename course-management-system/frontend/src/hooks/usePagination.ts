import { useState, useCallback, useMemo } from 'react';

export interface PaginationConfig {
  /** 当前页码 */
  current: number;
  /** 每页条数 */
  pageSize: number;
  /** 总条数 */
  total: number;
  /** 是否显示快速跳转 */
  showQuickJumper?: boolean;
  /** 是否显示每页条数选择器 */
  showSizeChanger?: boolean;
  /** 每页条数选项 */
  pageSizeOptions?: string[];
  /** 是否显示总数 */
  showTotal?: boolean;
  /** 总数显示函数 */
  showTotalText?: (total: number, range: [number, number]) => string;
}

export interface UsePaginationResult {
  /** 分页配置 */
  pagination: PaginationConfig;
  /** 改变页码 */
  changePage: (page: number) => void;
  /** 改变每页条数 */
  changePageSize: (pageSize: number) => void;
  /** 改变页码和每页条数 */
  changePagination: (page: number, pageSize?: number) => void;
  /** 设置总数 */
  setTotal: (total: number) => void;
  /** 重置分页 */
  reset: () => void;
  /** 跳转到第一页 */
  goToFirst: () => void;
  /** 跳转到最后一页 */
  goToLast: () => void;
  /** 上一页 */
  goToPrev: () => void;
  /** 下一页 */
  goToNext: () => void;
  /** 当前页的数据范围 */
  currentRange: [number, number];
  /** 总页数 */
  totalPages: number;
  /** 是否有上一页 */
  hasPrev: boolean;
  /** 是否有下一页 */
  hasNext: boolean;
}

/**
 * 分页Hook
 * @param initialConfig 初始配置
 * @returns 分页相关的状态和方法
 */
export function usePagination(
  initialConfig: Partial<PaginationConfig> = {}
): UsePaginationResult {
  const defaultConfig: PaginationConfig = {
    current: 1,
    pageSize: 20,
    total: 0,
    showQuickJumper: true,
    showSizeChanger: true,
    pageSizeOptions: ['10', '20', '50', '100'],
    showTotal: true,
    showTotalText: (total, range) => `第 ${range[0]}-${range[1]} 条，共 ${total} 条`,
    ...initialConfig,
  };

  const [pagination, setPagination] = useState<PaginationConfig>(defaultConfig);

  // 改变页码
  const changePage = useCallback((page: number) => {
    setPagination(prev => ({
      ...prev,
      current: Math.max(1, Math.min(page, Math.ceil(prev.total / prev.pageSize))),
    }));
  }, []);

  // 改变每页条数
  const changePageSize = useCallback((pageSize: number) => {
    setPagination(prev => {
      const newTotalPages = Math.ceil(prev.total / pageSize);
      const newCurrent = prev.current > newTotalPages ? newTotalPages : prev.current;
      return {
        ...prev,
        pageSize,
        current: Math.max(1, newCurrent),
      };
    });
  }, []);

  // 改变页码和每页条数
  const changePagination = useCallback((page: number, pageSize?: number) => {
    setPagination(prev => {
      const newPageSize = pageSize || prev.pageSize;
      const maxPage = Math.ceil(prev.total / newPageSize);
      return {
        ...prev,
        current: Math.max(1, Math.min(page, maxPage)),
        pageSize: newPageSize,
      };
    });
  }, []);

  // 设置总数
  const setTotal = useCallback((total: number) => {
    setPagination(prev => {
      const maxPage = Math.ceil(total / prev.pageSize);
      return {
        ...prev,
        total,
        current: prev.current > maxPage ? Math.max(1, maxPage) : prev.current,
      };
    });
  }, []);

  // 重置分页
  const reset = useCallback(() => {
    setPagination(defaultConfig);
  }, [defaultConfig]);

  // 计算属性
  const totalPages = useMemo(() => {
    return Math.ceil(pagination.total / pagination.pageSize);
  }, [pagination.total, pagination.pageSize]);

  const currentRange = useMemo((): [number, number] => {
    const start = (pagination.current - 1) * pagination.pageSize + 1;
    const end = Math.min(pagination.current * pagination.pageSize, pagination.total);
    return [start, end];
  }, [pagination.current, pagination.pageSize, pagination.total]);

  const hasPrev = useMemo(() => {
    return pagination.current > 1;
  }, [pagination.current]);

  const hasNext = useMemo(() => {
    return pagination.current < totalPages;
  }, [pagination.current, totalPages]);

  // 导航方法
  const goToFirst = useCallback(() => {
    changePage(1);
  }, [changePage]);

  const goToLast = useCallback(() => {
    changePage(totalPages);
  }, [changePage, totalPages]);

  const goToPrev = useCallback(() => {
    if (hasPrev) {
      changePage(pagination.current - 1);
    }
  }, [changePage, pagination.current, hasPrev]);

  const goToNext = useCallback(() => {
    if (hasNext) {
      changePage(pagination.current + 1);
    }
  }, [changePage, pagination.current, hasNext]);

  return {
    pagination,
    changePage,
    changePageSize,
    changePagination,
    setTotal,
    reset,
    goToFirst,
    goToLast,
    goToPrev,
    goToNext,
    currentRange,
    totalPages,
    hasPrev,
    hasNext,
  };
}

/**
 * 表格分页Hook
 * @param initialConfig 初始配置
 * @returns 表格分页相关的状态和方法
 */
export function useTablePagination(
  initialConfig: Partial<PaginationConfig> = {}
) {
  const paginationResult = usePagination(initialConfig);

  // Ant Design Table 分页配置
  const tablePagination = useMemo(() => ({
    current: paginationResult.pagination.current,
    pageSize: paginationResult.pagination.pageSize,
    total: paginationResult.pagination.total,
    showQuickJumper: paginationResult.pagination.showQuickJumper,
    showSizeChanger: paginationResult.pagination.showSizeChanger,
    pageSizeOptions: paginationResult.pagination.pageSizeOptions,
    showTotal: paginationResult.pagination.showTotalText,
    onChange: paginationResult.changePage,
    onShowSizeChange: (current: number, size: number) => {
      paginationResult.changePagination(current, size);
    },
  }), [paginationResult]);

  return {
    ...paginationResult,
    tablePagination,
  };
}

/**
 * 无限滚动分页Hook
 * @param pageSize 每页条数
 * @returns 无限滚动相关的状态和方法
 */
export function useInfiniteScroll(pageSize: number = 20) {
  const [currentPage, setCurrentPage] = useState(1);
  const [hasMore, setHasMore] = useState(true);
  const [total, setTotal] = useState(0);

  const loadMore = useCallback(() => {
    if (hasMore) {
      setCurrentPage(prev => prev + 1);
    }
  }, [hasMore]);

  const reset = useCallback(() => {
    setCurrentPage(1);
    setHasMore(true);
    setTotal(0);
  }, []);

  const updateTotal = useCallback((newTotal: number) => {
    setTotal(newTotal);
    const maxPage = Math.ceil(newTotal / pageSize);
    setHasMore(currentPage < maxPage);
  }, [currentPage, pageSize]);

  const loadedCount = useMemo(() => {
    return Math.min(currentPage * pageSize, total);
  }, [currentPage, pageSize, total]);

  return {
    currentPage,
    pageSize,
    hasMore,
    total,
    loadedCount,
    loadMore,
    reset,
    setTotal: updateTotal,
  };
}

export default usePagination;
