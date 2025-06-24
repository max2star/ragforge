import { useKnowledgeBaseId } from '@/hooks/knowledge-hooks';
import {
  useNavigateWithFromState,
  useSecondPathName,
  useThirdPathName,
} from '@/hooks/route-hook';
import { Breadcrumb, Layout } from 'antd';
import { ItemType } from 'antd/es/breadcrumb/Breadcrumb';
import { useMemo } from 'react';
import { useTranslation } from 'react-i18next';
import { Link, Outlet } from 'umi';
import Siderbar from './components/knowledge-sidebar';
import { KnowledgeDatasetRouteKey, KnowledgeRouteKey } from './constant';

const { Content } = Layout;

const KnowledgeAdding = () => {
  const knowledgeBaseId = useKnowledgeBaseId();

  const { t } = useTranslation();
  const activeKey: KnowledgeRouteKey =
    (useSecondPathName() as KnowledgeRouteKey) || KnowledgeRouteKey.Dataset;

  const datasetActiveKey: KnowledgeDatasetRouteKey =
    useThirdPathName() as KnowledgeDatasetRouteKey;

  const gotoList = useNavigateWithFromState();

  const breadcrumbItems: ItemType[] = useMemo(() => {
    const items: ItemType[] = [
      {
        title: (
          <a onClick={() => gotoList('/knowledge')}>
            {t('header.knowledgeBase')}
          </a>
        ),
      },
      {
        title: datasetActiveKey ? (
          <Link
            to={`/knowledge/${KnowledgeRouteKey.Dataset}?id=${knowledgeBaseId}`}
          >
            {t(`knowledgeDetails.${activeKey}`)}
          </Link>
        ) : (
          t(`knowledgeDetails.${activeKey}`)
        ),
      },
    ];

    if (datasetActiveKey) {
      items.push({
        title: t(`knowledgeDetails.${datasetActiveKey}`),
      });
    }

    return items;
  }, [activeKey, datasetActiveKey, gotoList, knowledgeBaseId, t]);

  return (
    <Layout style={{ width: '100%', background: '#f0f2f5' }}>
      <Siderbar />
      <Content style={{ padding: '24px', minHeight: 280 }}>
        <Breadcrumb items={breadcrumbItems} style={{ marginBottom: 16 }} />
        <div style={{ background: '#fff', padding: 24, borderRadius: 6 }}>
          <Outlet />
        </div>
      </Content>
    </Layout>
  );
};

export default KnowledgeAdding;
