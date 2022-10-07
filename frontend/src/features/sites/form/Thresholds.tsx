import { Checkbox, Form, Slider } from 'antd';

const formatter = (value?: number) => {
  if (value == null) return;
  const displayedValue = Math.round(value * 100); // fix floating point math bugs
  return `${displayedValue}%`;
};

export function DocumentTypeThreshold() {
  const form = Form.useFormInstance();
  const docTypeThresholdOverride = Form.useWatch('doc_type_threshold_override', form);
  return (
    <>
      <Form.Item
        name="doc_type_threshold_override"
        label="Document Type Threshold Override"
        valuePropName="checked"
      >
        <Checkbox />
      </Form.Item>
      {docTypeThresholdOverride ? (
        <Form.Item name="doc_type_threshold" label="Document Type Threshold">
          <Slider
            defaultValue={0.75}
            min={0}
            max={1}
            step={0.01}
            tipFormatter={formatter}
            tooltip={{
              open: true,
              placement: 'left',
              getPopupContainer: (triggerNode) => triggerNode.parentElement ?? triggerNode, // fixes tooltip to be inline with element -- https://github.com/ant-design/ant-design/issues/25117#issuecomment-873747921
            }}
          />
        </Form.Item>
      ) : null}
    </>
  );
}

export function LineageThreshold() {
  const form = Form.useFormInstance();
  const lineageThresholdOverride = Form.useWatch('lineage_threshold_override', form);
  return (
    <>
      <Form.Item
        name="lineage_threshold_override"
        label="Lineage Threshold Override"
        valuePropName="checked"
      >
        <Checkbox />
      </Form.Item>
      {lineageThresholdOverride ? (
        <Form.Item name="lineage_threshold" label="Lineage Threshold">
          <Slider
            defaultValue={0.75}
            min={0}
            max={1}
            step={0.01}
            tipFormatter={formatter}
            tooltip={{
              open: true,
              placement: 'left',
              getPopupContainer: (triggerNode) => triggerNode.parentElement ?? triggerNode, // fixes tooltip to be inline with element -- https://github.com/ant-design/ant-design/issues/25117#issuecomment-873747921
            }}
          />
        </Form.Item>
      ) : null}
    </>
  );
}
