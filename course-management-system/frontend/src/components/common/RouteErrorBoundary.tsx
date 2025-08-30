import { Component, ErrorInfo, ReactNode } from 'react';
import { Result, Button } from 'antd';
import { HomeOutlined, ReloadOutlined } from '@ant-design/icons';

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

class RouteErrorBoundary extends Component<Props, State> {
  constructor(props: Props) {
    super(props);
    this.state = { hasError: false };
  }

  static getDerivedStateFromError(error: Error): State {
    // 更新 state 使下一次渲染能够显示降级后的 UI
    return { hasError: true, error };
  }

  componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    // 你同样可以将错误日志上报给服务器
    console.error('Route Error Boundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/dashboard';
  };

  render() {
    if (this.state.hasError) {
      // 如果有自定义的 fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // 默认的错误页面
      return (
        <div style={{ padding: '50px' }}>
          <Result
            status="500"
            title="页面加载失败"
            subTitle="抱歉，页面加载时出现了错误。请尝试刷新页面或返回首页。"
            extra={[
              <Button 
                type="primary" 
                icon={<ReloadOutlined />} 
                onClick={this.handleReload}
                key="reload"
              >
                刷新页面
              </Button>,
              <Button 
                icon={<HomeOutlined />} 
                onClick={this.handleGoHome}
                key="home"
              >
                返回首页
              </Button>,
            ]}
          />
          
          {/* 开发环境下显示错误详情 */}
          {process.env.NODE_ENV === 'development' && this.state.error && (
            <div style={{ 
              marginTop: '20px', 
              padding: '20px', 
              backgroundColor: '#f5f5f5',
              borderRadius: '4px',
              fontSize: '12px',
              fontFamily: 'monospace',
              whiteSpace: 'pre-wrap',
              overflow: 'auto',
              maxHeight: '300px'
            }}>
              <h4>错误详情（仅开发环境显示）：</h4>
              <div style={{ color: '#d32f2f' }}>
                {this.state.error.toString()}
              </div>
              {this.state.errorInfo && (
                <div style={{ marginTop: '10px', color: '#666' }}>
                  {this.state.errorInfo.componentStack}
                </div>
              )}
            </div>
          )}
        </div>
      );
    }

    return this.props.children;
  }
}

export default RouteErrorBoundary;
