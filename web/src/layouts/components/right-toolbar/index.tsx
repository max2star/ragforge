import { useTranslate } from '@/hooks/common-hooks';
import { CrownOutlined, DownOutlined, GithubOutlined } from '@ant-design/icons';
import { Dropdown, MenuProps, Space } from 'antd';
import camelCase from 'lodash/camelCase';
import React, { useCallback, useMemo } from 'react';
import User from '../user';

import { LanguageList, LanguageMap } from '@/constants/common';
import { useChangeLanguage } from '@/hooks/logic-hooks';
import { useFetchUserInfo, useListTenant } from '@/hooks/user-setting-hooks';
import { TenantRole } from '@/pages/user-setting/constants';
import { BellRing } from 'lucide-react';
import { useNavigate } from 'umi';
import styled from './index.less';

const Circle = ({ children, ...restProps }: React.PropsWithChildren) => {
  return (
    <div {...restProps} className={styled.circle}>
      {children}
    </div>
  );
};

const handleGithubCLick = () => {
  window.open('https://github.com/infiniflow/ragflow', 'target');
};

const RightToolBar = () => {
  const { t } = useTranslate('common');
  const changeLanguage = useChangeLanguage();
  const navigate = useNavigate();

  const {
    data: { language = 'English' },
  } = useFetchUserInfo();

  const handleItemClick: MenuProps['onClick'] = ({ key }) => {
    changeLanguage(key);
  };

  const { data } = useListTenant();

  const showBell = useMemo(() => {
    return data.some((x) => x.role === TenantRole.Invite);
  }, [data]);

  const items: MenuProps['items'] = LanguageList.map((x) => ({
    key: x,
    label: <span>{LanguageMap[x as keyof typeof LanguageMap]}</span>,
  })).reduce<MenuProps['items']>((pre, cur) => {
    return [...pre!, { type: 'divider' }, cur];
  }, []);

  const handleBellClick = useCallback(() => {
    navigate('/user-setting/team');
  }, [navigate]);

  return (
    <div className={styled.toolbarWrapper}>
      <Space wrap size={16}>
        <a
          href="https://www.matrixstar.tech/h-col-108.html"
          target="_blank"
          rel="noopener noreferrer"
          style={{
            color: '#6a11cb',
            display: 'flex',
            alignItems: 'center',
            fontWeight: 'bold',
          }}
        >
          <CrownOutlined style={{ marginRight: 8 }} />
          购买专业版
        </a>
        <Dropdown menu={{ items, onClick: handleItemClick }} placement="bottom">
          <Space className={styled.language}>
            <b style={{ color: '#1f1f1f' }}>{t(camelCase(language))}</b>
            <DownOutlined style={{ color: '#1f1f1f' }} />
          </Space>
        </Dropdown>
        <Circle>
          <GithubOutlined onClick={handleGithubCLick} />
        </Circle>
        {showBell && (
          <Circle>
            <div className="relative" onClick={handleBellClick}>
              <BellRing className="size-4 " />
              <span className="absolute size-1 rounded -right-1 -top-1 bg-red-600"></span>
            </div>
          </Circle>
        )}
        <User></User>
      </Space>
    </div>
  );
};

export default RightToolBar;
