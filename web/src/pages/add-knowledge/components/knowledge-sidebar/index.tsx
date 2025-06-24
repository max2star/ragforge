import { ReactComponent as ConfigurationIcon } from '@/assets/svg/knowledge-configration.svg';
import { ReactComponent as DatasetIcon } from '@/assets/svg/knowledge-dataset.svg';
import { ReactComponent as TestingIcon } from '@/assets/svg/knowledge-testing.svg';
import {
  useFetchKnowledgeBaseConfiguration,
  useFetchKnowledgeGraph,
} from '@/hooks/knowledge-hooks';
import {
  useGetKnowledgeSearchParams,
  useSecondPathName,
} from '@/hooks/route-hook';
import { BookOutlined } from '@ant-design/icons';
import { Layout, Menu, MenuProps, Space, Typography } from 'antd';
import { useCallback, useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'umi';
import { KnowledgeRouteKey } from '../../constant';

import { isEmpty } from 'lodash';
import { GitGraph } from 'lucide-react';

const { Sider } = Layout;
const { Text } = Typography;

const KnowledgeSidebar = () => {
  let navigate = useNavigate();
  const activeKey = useSecondPathName();
  const { knowledgeId } = useGetKnowledgeSearchParams();

  const { t } = useTranslation();
  const { data: knowledgeDetails } = useFetchKnowledgeBaseConfiguration();

  const handleSelect: MenuProps['onSelect'] = (e) => {
    navigate(`/knowledge/${e.key}?id=${knowledgeId}`);
  };

  const { data } = useFetchKnowledgeGraph();

  type MenuItem = Required<MenuProps>['items'][number];

  const getItem = useCallback(
    (
      label: string,
      key: React.Key,
      icon?: React.ReactNode,
      disabled?: boolean,
      children?: MenuItem[],
      type?: 'group',
    ): MenuItem => {
      return {
        key,
        icon,
        children,
        label: t(`knowledgeDetails.${label}`),
        type,
        disabled,
      } as MenuItem;
    },
    [t],
  );

  const items: MenuItem[] = useMemo(() => {
    const list = [
      getItem(
        KnowledgeRouteKey.Dataset,
        KnowledgeRouteKey.Dataset,
        <DatasetIcon width={16} height={16} />,
      ),
      getItem(
        KnowledgeRouteKey.Testing,
        KnowledgeRouteKey.Testing,
        <TestingIcon width={16} height={16} />,
      ),
      getItem(
        KnowledgeRouteKey.Configuration,
        KnowledgeRouteKey.Configuration,
        <ConfigurationIcon width={16} height={16} />,
      ),
    ];

    if (!isEmpty(data?.graph)) {
      list.push(
        getItem(
          KnowledgeRouteKey.KnowledgeGraph,
          KnowledgeRouteKey.KnowledgeGraph,
          <GitGraph size={16} />,
        ),
      );
    }

    return list;
  }, [data, getItem]);

  return (
    <Sider width={200} style={{ background: '#fff' }}>
      <div style={{ padding: '24px 16px 16px 16px' }}>
        <Space size={8} direction="vertical" style={{ width: '100%' }}>
          <div
            style={{ display: 'flex', alignItems: 'center', marginBottom: 4 }}
          >
            <BookOutlined style={{ marginRight: 8, fontSize: 16 }} />
            <Text strong style={{ fontSize: 14, lineHeight: '22px' }}>
              {knowledgeDetails.name}
            </Text>
          </div>
        </Space>
        <Text type="secondary" style={{ fontSize: 12, lineHeight: '16px' }}>
          {knowledgeDetails.description}
        </Text>
      </div>
      <div
        style={{ height: 1, background: '#f0f0f0', margin: '0 16px 16px 16px' }}
      ></div>
      <Menu
        mode="inline"
        selectedKeys={[activeKey]}
        items={items}
        onSelect={handleSelect}
        style={{ height: 'calc(100% - 120px)', borderRight: 0 }}
      />
    </Sider>
  );
};

export default KnowledgeSidebar;
