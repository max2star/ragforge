import { Layout } from 'antd';
import { useState } from 'react';
import { ReactFlowProvider } from 'reactflow';
import FlowCanvas from './canvas';
import Sider from './flow-sider';
import FlowHeader from './header';
import { useFetchDataOnMount } from './hooks';

const { Content } = Layout;

function RagFlow() {
  const [collapsed, setCollapsed] = useState(false);

  useFetchDataOnMount();

  return (
    <Layout>
      <ReactFlowProvider>
        <Sider setCollapsed={setCollapsed} collapsed={collapsed}></Sider>
        <Layout>
          <FlowHeader></FlowHeader>
          <Content style={{ margin: 0 }}>
            <FlowCanvas sideWidth={collapsed ? 0 : 200}></FlowCanvas>
          </Content>
        </Layout>
      </ReactFlowProvider>
    </Layout>
  );
}

export default RagFlow;
