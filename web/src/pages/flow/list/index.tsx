import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { Card, Empty, Flex, Input, Skeleton, Space, Spin } from 'antd';
import AgentTemplateModal from './agent-template-modal';
import FlowCard from './flow-card';
import { useFetchDataOnMount, useSaveFlow } from './hooks';

import { useTranslate } from '@/hooks/common-hooks';
import { useMemo } from 'react';
import InfiniteScroll from 'react-infinite-scroll-component';
import styles from './index.less';

const CreateFlowCard = ({
  onClick,
  className,
}: {
  onClick: () => void;
  className: string;
}) => {
  return (
    <Card className={className} onClick={onClick}>
      <PlusOutlined style={{ fontSize: 24 }} />
      <span>创建工作流</span>
    </Card>
  );
};

const FlowList = () => {
  const {
    showFlowSettingModal,
    hideFlowSettingModal,
    flowSettingVisible,
    flowSettingLoading,
    onFlowOk,
  } = useSaveFlow();
  const { t } = useTranslate('flow');

  const {
    data,
    loading,
    searchString,
    handleInputChange,
    fetchNextPage,
    hasNextPage,
  } = useFetchDataOnMount();

  const nextList = useMemo(() => {
    const list =
      data?.pages?.flatMap((x) => (Array.isArray(x.kbs) ? x.kbs : [])) ?? [];
    return list;
  }, [data?.pages]);

  const total = useMemo(() => {
    return data?.pages.at(-1).total ?? 0;
  }, [data?.pages]);

  return (
    <Flex className={styles.flowPage} vertical flex={1}>
      <div className={styles.headerWrapper}>
        <span className={styles.title}>我的工作流</span>
        <Space size={'large'}>
          <Input
            placeholder={t('searchAgentPlaceholder')}
            value={searchString}
            allowClear
            onChange={handleInputChange}
            prefix={<SearchOutlined />}
          />
        </Space>
      </div>
      <div className={styles.contentWrapper} id="flow-scroll-container">
        <InfiniteScroll
          dataLength={nextList?.length ?? 0}
          next={fetchNextPage}
          hasMore={hasNextPage}
          loader={<Skeleton avatar paragraph={{ rows: 1 }} active />}
          endMessage={null}
          scrollableTarget="flow-scroll-container"
        >
          <Spin spinning={loading}>
            <Flex
              gap={'large'}
              wrap="wrap"
              className={styles.flowCardContainer}
            >
              <CreateFlowCard
                onClick={showFlowSettingModal}
                className={styles.createCard}
              />
              {nextList.map((item) => {
                return <FlowCard item={item} key={item.id}></FlowCard>;
              })}
            </Flex>
            {!nextList?.length && !searchString && (
              <Empty className={styles.knowledgeEmpty}></Empty>
            )}
          </Spin>
        </InfiniteScroll>
      </div>
      {flowSettingVisible && (
        <AgentTemplateModal
          visible={flowSettingVisible}
          onOk={onFlowOk}
          loading={flowSettingLoading}
          hideModal={hideFlowSettingModal}
        ></AgentTemplateModal>
      )}
    </Flex>
  );
};

export default FlowList;
