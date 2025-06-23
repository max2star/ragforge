import { useInfiniteFetchKnowledgeList } from '@/hooks/knowledge-hooks';
import { useFetchUserInfo } from '@/hooks/user-setting-hooks';
import { PlusOutlined, SearchOutlined } from '@ant-design/icons';
import { Card, Flex, Input, Skeleton, Space, Spin } from 'antd';
import { useTranslation } from 'react-i18next';
import InfiniteScroll from 'react-infinite-scroll-component';
import { useSaveKnowledge } from './hooks';
import KnowledgeCard from './knowledge-card';
import KnowledgeCreatingModal from './knowledge-creating-modal';

import { useMemo } from 'react';
import styles from './index.less';

const CreateKnowledgeCard = ({
  onClick,
  className,
}: {
  onClick: () => void;
  className: string;
}) => {
  return (
    <Card className={className} onClick={onClick}>
      <PlusOutlined style={{ fontSize: 24 }} />
      <span>创建知识库</span>
    </Card>
  );
};

const KnowledgeList = () => {
  const { data: userInfo } = useFetchUserInfo();
  const { t } = useTranslation('translation', { keyPrefix: 'knowledgeList' });
  const {
    visible,
    hideModal,
    showModal,
    onCreateOk,
    loading: creatingLoading,
  } = useSaveKnowledge();
  const {
    fetchNextPage,
    data,
    hasNextPage,
    searchString,
    handleInputChange,
    loading,
  } = useInfiniteFetchKnowledgeList();

  const nextList = useMemo(() => {
    const list =
      data?.pages?.flatMap((x) => (Array.isArray(x.kbs) ? x.kbs : [])) ?? [];
    return list;
  }, [data?.pages]);

  const total = useMemo(() => {
    return data?.pages.at(-1)?.total ?? 0;
  }, [data?.pages]);

  return (
    <Flex className={styles.knowledge} vertical flex={1} id="scrollableDiv">
      <div className={styles.topWrapper}>
        <span className={styles.title}>知识库</span>

        <Space size={'large'} className={styles.actionButtons}>
          <Input
            placeholder={t('searchKnowledgePlaceholder')}
            value={searchString}
            style={{ width: 220 }}
            allowClear
            onChange={handleInputChange}
            prefix={<SearchOutlined />}
          />
        </Space>
      </div>
      <Spin spinning={loading}>
        <InfiniteScroll
          dataLength={nextList?.length ?? 0}
          next={fetchNextPage}
          hasMore={hasNextPage}
          loader={<Skeleton avatar paragraph={{ rows: 1 }} active />}
          endMessage={null}
          scrollableTarget="scrollableDiv"
        >
          <Flex
            gap={'large'}
            wrap="wrap"
            className={styles.knowledgeCardContainer}
          >
            <CreateKnowledgeCard
              onClick={showModal}
              className={styles.createCard}
            />
            {nextList.map((item: any, index: number) => {
              return (
                <KnowledgeCard
                  item={item}
                  key={`${item?.name}-${index}`}
                ></KnowledgeCard>
              );
            })}
          </Flex>
        </InfiniteScroll>
      </Spin>
      <KnowledgeCreatingModal
        loading={creatingLoading}
        visible={visible}
        hideModal={hideModal}
        onOk={onCreateOk}
      ></KnowledgeCreatingModal>
    </Flex>
  );
};

export default KnowledgeList;
