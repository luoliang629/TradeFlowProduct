import { Spin } from 'antd';
import type { SpinSize } from 'antd/es/spin';

interface LoadingSpinnerProps {
  size?: SpinSize;
  tip?: string;
  className?: string;
}

const LoadingSpinner: React.FC<LoadingSpinnerProps> = ({
  size = 'default',
  tip,
  className = '',
}) => {
  return (
    <div className={`flex items-center justify-center ${className}`}>
      <Spin size={size} tip={tip} />
    </div>
  );
};

export default LoadingSpinner;