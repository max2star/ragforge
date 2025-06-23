import { formatDate } from '@/utils/date';
import { Badge, Card, Space } from 'antd';
import { useNavigate } from 'umi';

import OperateDropdown from '@/components/operate-dropdown';
import { useTheme } from '@/components/theme-provider';
import { useDeleteFlow } from '@/hooks/flow-hooks';
import { useFetchUserInfo } from '@/hooks/user-setting-hooks';
import { IFlow } from '@/interfaces/database/flow';
import { EllipsisOutlined } from '@ant-design/icons';
import classNames from 'classnames';
import { useCallback } from 'react';
import { useTranslation } from 'react-i18next';
import GraphAvatar from '../graph-avatar';
import styles from './index.less';

interface IProps {
  item: IFlow;
  onDelete?: (string: string) => void;
}

const FlowCard = ({ item }: IProps) => {
  const navigate = useNavigate();
  const { deleteFlow } = useDeleteFlow();
  const { data: userInfo } = useFetchUserInfo();
  const { t } = useTranslation();
  const { theme } = useTheme();

  const removeFlow = useCallback(() => {
    return deleteFlow([item.id]);
  }, [deleteFlow, item]);

  const handleCardClick = (e: React.MouseEvent) => {
    if (
      (e.target as HTMLElement).closest('.ant-dropdown-trigger') ||
      (e.target as HTMLElement).closest('.ant-dropdown-menu-item')
    ) {
      return;
    }
    navigate(`/flow/${item.id}`);
  };

  return (
    <Badge.Ribbon
      text={item?.nickname}
      color={userInfo?.nickname === item?.nickname ? '#1677ff' : 'pink'}
      className={classNames(styles.ribbon, {
        [styles.hideRibbon]: item.permission !== 'team',
      })}
    >
      <Card
        className={styles.card}
        onClick={handleCardClick}
        data-theme={theme}
      >
        <div className={styles.container}>
          <div className={styles.header}>
            <div className={styles.titleSection}>
              <GraphAvatar avatar={item.avatar}></GraphAvatar>
              <span
                className={theme === 'dark' ? styles.titledark : styles.title}
              >
                {item.name}
              </span>
            </div>
            <OperateDropdown
              deleteItem={removeFlow}
              items={[
                {
                  key: '1',
                  label: 'run',
                },
              ]}
            >
              <EllipsisOutlined className={styles.ellipsis} />
            </OperateDropdown>
          </div>

          <div className={styles.body}>
            <p
              className={
                theme === 'dark' ? styles.descriptiondark : styles.description
              }
            >
              {item.description || '暂无描述'}
            </p>
          </div>

          <div className={styles.footer}>
            <Space className={styles.stats}>
              <span>创建者: {item.nickname}</span>
            </Space>
            <span className={styles.date}>{formatDate(item.update_time)}</span>
          </div>
        </div>
      </Card>
    </Badge.Ribbon>
  );
};

export default FlowCard;
