using UnityEngine;
using UnityEngine.UIElements;

/// <summary>
/// Wires the UI Toolkit panel to CameraController.
/// Attach to the same GameObject as your UIDocument component.
/// Set the UIDocument's Source Asset to CameraTransformPanel.uxml.
/// Drag your camera GameObject into the Controller field in the Inspector.
/// </summary>
public class CameraTransformUI : MonoBehaviour
{
    [Tooltip("The GameObject with CameraTransformController attached")]
    public CameraController controller;

    private Label _positionReadout;
    private Vector3Field _offsetField;
    private Vector3Field _scaleField;
    private Vector3Field _rotationField;
    private Label _timestampReadout;

    void OnEnable()
    {
        var root = GetComponent<UIDocument>().rootVisualElement;

        _positionReadout = root.Q<Label>("position-readout");
        _offsetField     = root.Q<Vector3Field>("offset-field");
        _scaleField      = root.Q<Vector3Field>("scale-field");
        _rotationField   = root.Q<Vector3Field>("rotation-field");

        // Initialise fields from current controller values
        _offsetField.value   = controller.positionOffset;
        _scaleField.value    = controller.positionScale;
        _rotationField.value = controller.rotationOffset;

        // Push changes from UI → controller
        _offsetField.RegisterValueChangedCallback(evt =>
            controller.positionOffset = evt.newValue);

        _scaleField.RegisterValueChangedCallback(evt =>
            controller.positionScale = evt.newValue);

        _rotationField.RegisterValueChangedCallback(evt =>
            controller.rotationOffset = evt.newValue);

        _timestampReadout = root.Q<Label>("timestamp-readout");
    }

    void Update()
    {
        // Toggle panel visibility with Tab
        if (Input.GetKeyDown(KeyCode.Tab))
        {
            var panel = GetComponent<UIDocument>().rootVisualElement.Q("panel");
            bool visible = panel.style.display == DisplayStyle.Flex;
            panel.style.display = visible ? DisplayStyle.None : DisplayStyle.Flex;
        }

        // Only update readout if visible (minor optimisation)
       if (_positionReadout != null && 
           _positionReadout.panel != null)
       {
           Vector3 p = controller.TranslatedPosition;
           _positionReadout.text = $"x: {p.x:F3}   y: {p.y:F3}   z: {p.z:F3}";
       }
       _timestampReadout.text = controller.LastTimestamp.ToString();
    }
}
