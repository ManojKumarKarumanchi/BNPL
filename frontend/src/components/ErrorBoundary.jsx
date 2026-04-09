import React from 'react';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = { hasError: false, error: null, errorInfo: null };
  }

  static getDerivedStateFromError(error) {
    return { hasError: true };
  }

  componentDidCatch(error, errorInfo) {
    console.error('ErrorBoundary caught an error:', error, errorInfo);
    this.setState({
      error,
      errorInfo
    });
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="min-h-screen flex items-center justify-center bg-gray-50 px-4">
          <div className="max-w-md w-full bg-white rounded-lg shadow-xl p-6 border border-red-200">
            <div className="flex items-center gap-3 mb-4">
              <div className="flex-shrink-0">
                <svg className="w-8 h-8 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
                </svg>
              </div>
              <div>
                <h2 className="text-lg font-bold text-gray-900">Oops! Something went wrong</h2>
                <p className="text-sm text-gray-600 mt-1">
                  The application encountered an unexpected error.
                </p>
              </div>
            </div>

            {this.state.error && (
              <div className="mt-4 p-3 bg-red-50 rounded border border-red-200">
                <p className="text-xs font-mono text-red-800 break-all">
                  {this.state.error.toString()}
                </p>
              </div>
            )}

            <div className="mt-6 flex gap-3">
              <button
                onClick={() => window.location.reload()}
                className="flex-1 bg-grabcredit-600 text-white px-4 py-2 rounded-lg hover:bg-grabcredit-700 transition-colors font-medium"
              >
                Reload Page
              </button>
              <button
                onClick={() => this.setState({ hasError: false, error: null, errorInfo: null })}
                className="flex-1 bg-gray-200 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-300 transition-colors font-medium"
              >
                Try Again
              </button>
            </div>

            <p className="mt-4 text-xs text-gray-500 text-center">
              If this problem persists, please contact support.
            </p>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
