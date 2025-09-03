import { Component, ErrorInfo, ReactNode } from 'react';
import { Result, Button, Typography } from 'antd';
import { BugOutlined, ReloadOutlined, HomeOutlined } from '@ant-design/icons';

const { Paragraph, Text } = Typography;

interface Props {
  children: ReactNode;
  fallback?: ReactNode;
}

interface State {
  hasError: boolean;
  error?: Error;
  errorInfo?: ErrorInfo;
}

class ErrorBoundary extends Component<Props, State> {
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
    console.error('Error Boundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo,
    });
  }

  handleReload = () => {
    window.location.reload();
  };

  handleGoHome = () => {
    window.location.href = '/';
  };

  render() {
    if (this.state.hasError) {
      // 如果有自定义的 fallback，使用它
      if (this.props.fallback) {
        return this.props.fallback;
      }

      // 默认的错误页面
      return (
        <div style={{ padding: '50px', maxWidth: '800px', margin: '0 auto' }}>
          <Result
            status="error"
            title="应用程序发生错误"
            subTitle="抱歉，应用程序遇到了意外错误。我们的团队已被通知此问题。"
            extra={[
              <Button 
                type="primary" 
                icon={<ReloadOutlined />} 
                onClick={this.handleReload}
                key="reload"
              >
                重新加载
              </Button>,
              <Button 
                icon={<HomeOutlined />} 
                onClick={this.handleGoHome}
                key="home"
              >
                返回首页
              </Button>,
            ]}
          >
            <div className="desc">
              <Paragraph>
                <Text strong>错误信息:</Text>
              </Paragraph>
              <Paragraph>
                {this.state.error?.toString()}
              </Paragraph>
              
              {/* 开发环境下显示错误详情 */}
              {process.env.NODE_ENV === 'development' && this.state.errorInfo && (
                <div style={{ 
                  marginTop: '20px', 
                  padding: '15px', 
                  backgroundColor: '#fff2f0',
                  border: '1px solid #ffccc7',
                  borderRadius: '4px',
                  fontSize: '12px',
                  fontFamily: 'monospace',
                  whiteSpace: 'pre-wrap',
                  overflow: 'auto',
                  maxHeight: '200px'
                }}>
                  <Paragraph>
                    <Text strong>错误堆栈:</Text>
                  </Paragraph>
                  <div style={{ color: '#d32f2f' }}>
                    {this.state.errorInfo.componentStack}
                  </div>
                </div>
              )}
            </div>
          </Result>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;