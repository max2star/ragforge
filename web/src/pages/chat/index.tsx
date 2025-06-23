import { ReactComponent as ChatAppCube } from '@/assets/svg/chat-app-cube.svg';
import RenameModal from '@/components/rename-modal';
import { DeleteOutlined, EditOutlined, PlusOutlined } from '@ant-design/icons';
import {
  Avatar,
  Button,
  Card,
  Divider,
  Dropdown,
  Flex,
  MenuProps,
  Space,
  Spin,
  Tag,
  Tooltip,
  Typography,
} from 'antd';
import { MenuItemProps } from 'antd/lib/menu/MenuItem';
import classNames from 'classnames';
import { useCallback, useState } from 'react';
import ChatConfigurationModal from './chat-configuration-modal';
import ChatContainer from './chat-container';
import {
  useDeleteConversation,
  useDeleteDialog,
  useEditDialog,
  useHandleItemHover,
  useRenameConversation,
  useSelectDerivedConversationList,
} from './hooks';

import EmbedModal from '@/components/api-service/embed-modal';
import { useShowEmbedModal } from '@/components/api-service/hooks';
import SvgIcon from '@/components/svg-icon';
import { useTheme } from '@/components/theme-provider';
import { SharedFrom } from '@/constants/chat';
import {
  useClickConversationCard,
  useClickDialogCard,
  useFetchNextDialogList,
  useGetChatSearchParams,
} from '@/hooks/chat-hooks';
import { useTranslate } from '@/hooks/common-hooks';
import { useSetSelectedRecord } from '@/hooks/logic-hooks';
import { IDialog } from '@/interfaces/database/chat';
import { MessageSquare, PictureInPicture2 } from 'lucide-react';
import styles from './index.less';

const { Text } = Typography;

const CreateAssistantCard = ({
  onClick,
  className,
}: {
  onClick: () => void;
  className: string;
}) => {
  return (
    <Card className={className} onClick={onClick}>
      <PlusOutlined style={{ fontSize: 24 }} />
      <span>新建助手</span>
    </Card>
  );
};

const AssistantCard = ({
  dialog,
  onClick,
  onMenuClick,
  isSelected,
  className,
}: {
  dialog: IDialog;
  onClick: () => void;
  onMenuClick: MenuProps['items'];
  isSelected: boolean;
  className: string;
}) => {
  const { theme } = useTheme();

  return (
    <Card
      className={classNames(className, {
        [styles.assistantCardSelected]: isSelected,
      })}
      onClick={onClick}
    >
      <div className={styles.container}>
        <div className={styles.header}>
          <div className={styles.titleSection}>
            <MessageSquare className={styles.assistantIcon} />
            <span
              className={theme === 'dark' ? styles.titledark : styles.title}
            >
              {dialog.name}
            </span>
          </div>
        </div>

        <div className={styles.body}>
          <p
            className={
              theme === 'dark' ? styles.descriptiondark : styles.description
            }
          >
            {dialog.description || '暂无描述'}
          </p>
        </div>

        <div className={styles.footer}>
          <Space className={styles.stats} split={'|'}>
            <span>0 对话数</span>
            <span>0 消息数</span>
          </Space>
          <Dropdown menu={{ items: onMenuClick }}>
            <ChatAppCube className={styles.cubeIcon} />
          </Dropdown>
        </div>
      </div>
    </Card>
  );
};

const Chat = () => {
  const { data: dialogList, loading: dialogLoading } = useFetchNextDialogList();
  const { onRemoveDialog } = useDeleteDialog();
  const { onRemoveConversation } = useDeleteConversation();
  const { handleClickDialog } = useClickDialogCard();
  const { handleClickConversation } = useClickConversationCard();
  const { dialogId, conversationId } = useGetChatSearchParams();
  const { theme } = useTheme();
  const {
    list: conversationList,
    addTemporaryConversation,
    loading: conversationLoading,
  } = useSelectDerivedConversationList();
  const { activated, handleItemEnter, handleItemLeave } = useHandleItemHover();
  const {
    activated: conversationActivated,
    handleItemEnter: handleConversationItemEnter,
    handleItemLeave: handleConversationItemLeave,
  } = useHandleItemHover();
  const {
    conversationRenameLoading,
    initialConversationName,
    onConversationRenameOk,
    conversationRenameVisible,
    hideConversationRenameModal,
    showConversationRenameModal,
  } = useRenameConversation();
  const {
    dialogSettingLoading,
    initialDialog,
    onDialogEditOk,
    dialogEditVisible,
    clearDialog,
    hideDialogEditModal,
    showDialogEditModal,
  } = useEditDialog();
  const { t } = useTranslate('chat');
  const { currentRecord, setRecord } = useSetSelectedRecord<IDialog>();
  const [controller, setController] = useState(new AbortController());
  const { showEmbedModal, hideEmbedModal, embedVisible, beta } =
    useShowEmbedModal();

  const handleAppCardEnter = (id: string) => () => {
    handleItemEnter(id);
  };

  const handleConversationCardEnter = (id: string) => () => {
    handleConversationItemEnter(id);
  };

  const handleShowChatConfigurationModal =
    (dialogId?: string): any =>
    (info: any) => {
      info?.domEvent?.preventDefault();
      info?.domEvent?.stopPropagation();
      showDialogEditModal(dialogId);
    };

  const handleRemoveDialog =
    (dialogId: string): MenuItemProps['onClick'] =>
    ({ domEvent }) => {
      domEvent.preventDefault();
      domEvent.stopPropagation();
      onRemoveDialog([dialogId]);
    };

  const handleShowOverviewModal =
    (dialog: IDialog): any =>
    (info: any) => {
      info?.domEvent?.preventDefault();
      info?.domEvent?.stopPropagation();
      setRecord(dialog);
      showEmbedModal();
    };

  const handleRemoveConversation =
    (conversationId: string): MenuItemProps['onClick'] =>
    ({ domEvent }) => {
      domEvent.preventDefault();
      domEvent.stopPropagation();
      onRemoveConversation([conversationId]);
    };

  const handleShowConversationRenameModal =
    (conversationId: string): MenuItemProps['onClick'] =>
    ({ domEvent }) => {
      domEvent.preventDefault();
      domEvent.stopPropagation();
      showConversationRenameModal(conversationId);
    };

  const handleDialogCardClick = useCallback(
    (dialogId: string) => () => {
      handleClickDialog(dialogId);
    },
    [handleClickDialog],
  );

  const handleConversationCardClick = useCallback(
    (conversationId: string, isNew: boolean) => () => {
      handleClickConversation(conversationId, isNew ? 'true' : '');
      setController((pre) => {
        pre.abort();
        return new AbortController();
      });
    },
    [handleClickConversation],
  );

  const handleCreateTemporaryConversation = useCallback(() => {
    addTemporaryConversation();
  }, [addTemporaryConversation]);

  const buildAppItems = (dialog: IDialog) => {
    const dialogId = dialog.id;

    const appItems: MenuProps['items'] = [
      {
        key: '1',
        onClick: handleShowChatConfigurationModal(dialogId),
        label: (
          <Space>
            <EditOutlined />
            {t('edit', { keyPrefix: 'common' })}
          </Space>
        ),
      },
      { type: 'divider' },
      {
        key: '2',
        onClick: handleRemoveDialog(dialogId),
        label: (
          <Space>
            <DeleteOutlined />
            {t('delete', { keyPrefix: 'common' })}
          </Space>
        ),
      },
      { type: 'divider' },
      {
        key: '3',
        onClick: handleShowOverviewModal(dialog),
        label: (
          <Space>
            <PictureInPicture2 className="size-4" />
            {t('embedIntoSite', { keyPrefix: 'common' })}
          </Space>
        ),
      },
    ];

    return appItems;
  };

  const buildConversationItems = (conversationId: string) => {
    const appItems: MenuProps['items'] = [
      {
        key: '1',
        onClick: handleShowConversationRenameModal(conversationId),
        label: (
          <Space>
            <EditOutlined />
            {t('rename', { keyPrefix: 'common' })}
          </Space>
        ),
      },
      { type: 'divider' },
      {
        key: '2',
        onClick: handleRemoveConversation(conversationId),
        label: (
          <Space>
            <DeleteOutlined />
            {t('delete', { keyPrefix: 'common' })}
          </Space>
        ),
      },
    ];

    return appItems;
  };

  // 如果选择了助手，显示对话界面
  if (dialogId) {
    return (
      <Flex className={styles.chatWrapper}>
        <Flex className={styles.chatAppWrapper}>
          <Flex flex={1} vertical>
            <Button type="primary" onClick={handleShowChatConfigurationModal()}>
              {t('createAssistant')}
            </Button>
            <Divider></Divider>
            <Flex className={styles.chatAppContent} vertical gap={10}>
              <Spin spinning={dialogLoading} wrapperClassName={styles.chatSpin}>
                {dialogList.map((x) => (
                  <Card
                    key={x.id}
                    hoverable
                    className={classNames(styles.chatAppCard, {
                      [theme === 'dark'
                        ? styles.chatAppCardSelectedDark
                        : styles.chatAppCardSelected]: dialogId === x.id,
                    })}
                    onMouseEnter={handleAppCardEnter(x.id)}
                    onMouseLeave={handleItemLeave}
                    onClick={handleDialogCardClick(x.id)}
                  >
                    <Flex justify="space-between" align="center">
                      <Space size={15}>
                        <Avatar src={x.icon} shape={'square'} />
                        <section>
                          <b>
                            <Text
                              ellipsis={{ tooltip: x.name }}
                              style={{ width: 130 }}
                            >
                              {x.name}
                            </Text>
                          </b>
                          <div>{x.description}</div>
                        </section>
                      </Space>
                      {activated === x.id && (
                        <section>
                          <Dropdown menu={{ items: buildAppItems(x) }}>
                            <ChatAppCube
                              className={styles.cubeIcon}
                            ></ChatAppCube>
                          </Dropdown>
                        </section>
                      )}
                    </Flex>
                  </Card>
                ))}
              </Spin>
            </Flex>
          </Flex>
        </Flex>
        <Divider type={'vertical'} className={styles.divider}></Divider>
        <Flex className={styles.chatTitleWrapper}>
          <Flex flex={1} vertical>
            <Flex
              justify={'space-between'}
              align="center"
              className={styles.chatTitle}
            >
              <Space>
                <b>{t('chat')}</b>
                <Tag>{conversationList.length}</Tag>
              </Space>
              <Tooltip title={t('newChat')}>
                <div>
                  <SvgIcon
                    name="plus-circle-fill"
                    width={20}
                    onClick={handleCreateTemporaryConversation}
                  ></SvgIcon>
                </div>
              </Tooltip>
            </Flex>
            <Divider></Divider>
            <Flex vertical gap={10} className={styles.chatTitleContent}>
              <Spin
                spinning={conversationLoading}
                wrapperClassName={styles.chatSpin}
              >
                {conversationList.map((x) => (
                  <Card
                    key={x.id}
                    hoverable
                    onClick={handleConversationCardClick(x.id, x.is_new)}
                    onMouseEnter={handleConversationCardEnter(x.id)}
                    onMouseLeave={handleConversationItemLeave}
                    className={classNames(styles.chatTitleCard, {
                      [theme === 'dark'
                        ? styles.chatTitleCardSelectedDark
                        : styles.chatTitleCardSelected]:
                        x.id === conversationId,
                    })}
                  >
                    <Flex justify="space-between" align="center">
                      <div>
                        <Text
                          ellipsis={{ tooltip: x.name }}
                          style={{ width: 150 }}
                        >
                          {x.name}
                        </Text>
                      </div>
                      {conversationActivated === x.id &&
                        x.id !== '' &&
                        !x.is_new && (
                          <section>
                            <Dropdown
                              menu={{ items: buildConversationItems(x.id) }}
                            >
                              <ChatAppCube
                                className={styles.cubeIcon}
                              ></ChatAppCube>
                            </Dropdown>
                          </section>
                        )}
                    </Flex>
                  </Card>
                ))}
              </Spin>
            </Flex>
          </Flex>
        </Flex>
        <Divider type={'vertical'} className={styles.divider}></Divider>
        <ChatContainer controller={controller}></ChatContainer>
        {dialogEditVisible && (
          <ChatConfigurationModal
            visible={dialogEditVisible}
            initialDialog={initialDialog}
            showModal={showDialogEditModal}
            hideModal={hideDialogEditModal}
            loading={dialogSettingLoading}
            onOk={onDialogEditOk}
            clearDialog={clearDialog}
          ></ChatConfigurationModal>
        )}
        <RenameModal
          visible={conversationRenameVisible}
          hideModal={hideConversationRenameModal}
          onOk={onConversationRenameOk}
          initialName={initialConversationName}
          loading={conversationRenameLoading}
        ></RenameModal>

        {embedVisible && (
          <EmbedModal
            visible={embedVisible}
            hideModal={hideEmbedModal}
            token={currentRecord.id}
            form={SharedFrom.Chat}
            beta={beta}
            isAgent={false}
          ></EmbedModal>
        )}
      </Flex>
    );
  }

  // 助手列表页面
  return (
    <Flex className={styles.assistantList} vertical flex={1}>
      <div className={styles.topWrapper}>
        <span className={styles.title}>聊天助手</span>
      </div>
      <Spin spinning={dialogLoading}>
        <Flex
          gap={'large'}
          wrap="wrap"
          className={styles.assistantCardContainer}
        >
          <CreateAssistantCard
            onClick={handleShowChatConfigurationModal()}
            className={styles.createCard}
          />
          {dialogList.map((dialog) => (
            <AssistantCard
              key={dialog.id}
              dialog={dialog}
              onClick={handleDialogCardClick(dialog.id)}
              onMenuClick={buildAppItems(dialog)}
              isSelected={false}
              className={styles.assistantCard}
            />
          ))}
        </Flex>
        {!dialogList?.length && (
          <div className={styles.assistantEmpty}>
            <span>暂无助手，快去创建一个吧</span>
          </div>
        )}
      </Spin>
      {dialogEditVisible && (
        <ChatConfigurationModal
          visible={dialogEditVisible}
          initialDialog={initialDialog}
          showModal={showDialogEditModal}
          hideModal={hideDialogEditModal}
          loading={dialogSettingLoading}
          onOk={onDialogEditOk}
          clearDialog={clearDialog}
        ></ChatConfigurationModal>
      )}
      <RenameModal
        visible={conversationRenameVisible}
        hideModal={hideConversationRenameModal}
        onOk={onConversationRenameOk}
        initialName={initialConversationName}
        loading={conversationRenameLoading}
      ></RenameModal>

      {embedVisible && (
        <EmbedModal
          visible={embedVisible}
          hideModal={hideEmbedModal}
          token={currentRecord.id}
          form={SharedFrom.Chat}
          beta={beta}
          isAgent={false}
        ></EmbedModal>
      )}
    </Flex>
  );
};

export default Chat;
