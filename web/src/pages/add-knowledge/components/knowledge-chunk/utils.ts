export type FormListItem = {
  frequency: number;
  tag: string;
};

export function transformTagFeaturesArrayToObject(
  list: Array<FormListItem> = [],
) {
  return list.reduce<Record<string, number>>((pre, cur) => {
    pre[cur.tag] = cur.frequency;

    return pre;
  }, {});
}

export function transformTagFeaturesObjectToArray(
  object: Record<string, number> = {},
) {
  return Object.keys(object).reduce<Array<FormListItem>>((pre, key) => {
    pre.push({ frequency: object[key], tag: key });

    return pre;
  }, []);
}

export function shouldRenderAsHTML(content: string): boolean {
  const htmlTagPattern = /<\/?[a-z][\s\S]*>/i;
  return htmlTagPattern.test(content);
}