import { KnowledgeRouteKey } from '@/constants/knowledge';
import { IKnowledge } from '@/interfaces/database/knowledge';
import { BookOutlined } from '@ant-design/icons';
import { Badge, Card, Space } from 'antd';
import classNames from 'classnames';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'umi';

import OperateDropdown from '@/components/operate-dropdown';
import { useTheme } from '@/components/theme-provider';
import { useDeleteKnowledge } from '@/hooks/knowledge-hooks';
import styles from './index.less';

interface IProps {
  item: IKnowledge;
}

const formatCharCount = (num: number) => {
  if (num > 1000) {
    return `${(num / 1000).toFixed(1)}k`;
  }
  return num;
};

const KnowledgeCard = ({ item }: IProps) => {
  const navigate = useNavigate();
  const { t } = useTranslation();
  const { theme } = useTheme();
  const { deleteKnowledge } = useDeleteKnowledge();

  const removeKnowledge = async () => {
    return deleteKnowledge(item.id);
  };

  const handleCardClick = (e: React.MouseEvent) => {
    if (
      (e.target as HTMLElement).closest('.ant-dropdown-trigger') ||
      (e.target as HTMLElement).closest('.ant-dropdown-menu-item')
    ) {
      return;
    }
    navigate(`/knowledge/${KnowledgeRouteKey.Dataset}?id=${item.id}`, {
      state: { from: 'list' },
    });
  };

  return (
    <Badge.Ribbon text={item?.parser_id} className={classNames(styles.ribbon)}>
      <Card
        className={styles.card}
        onClick={handleCardClick}
        data-theme={theme}
      >
        <div className={styles.container}>
          <div className={styles.header}>
            <div className={styles.titleSection}>
              <BookOutlined className={styles.knowledgeIcon} />
              <span
                className={theme === 'dark' ? styles.titledark : styles.title}
              >
                {item.name}
              </span>
            </div>
          </div>

          <div className={styles.body}>
            <p className={styles.creator}>创建者: {item.nickname}</p>
            <p
              className={
                theme === 'dark' ? styles.descriptiondark : styles.description
              }
            >
              {item.description || '暂无描述'}
            </p>
          </div>

          <div className={styles.footer}>
            <Space className={styles.stats} split={'|'}>
              <span>{item.doc_num || 0} 文档数</span>
              <span>{formatCharCount(item.char_num || 0)} 字符</span>
              <span>0 关联应用</span>
            </Space>
            <OperateDropdown deleteItem={removeKnowledge}></OperateDropdown>
          </div>
        </div>
      </Card>
    </Badge.Ribbon>
  );
};

export default KnowledgeCard;
