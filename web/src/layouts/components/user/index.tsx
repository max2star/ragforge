import { useFetchUserInfo } from '@/hooks/user-setting-hooks';
import { UserOutlined } from '@ant-design/icons';
import React from 'react';
import { history } from 'umi';

const App: React.FC = () => {
  const { data: userInfo } = useFetchUserInfo();

  const toSetting = () => {
    history.push('/user-setting');
  };

  return (
    <div
      onClick={toSetting}
      style={{
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'center',
        width: 32,
        height: 32,
        borderRadius: '50%',
        backgroundColor: '#e6f7ff',
        cursor: 'pointer',
      }}
    >
      <UserOutlined style={{ color: '#1890ff', fontSize: 18 }} />
    </div>
  );
};

export default App;
