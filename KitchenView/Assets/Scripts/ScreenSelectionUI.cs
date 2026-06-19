using UnityEngine;
using UnityEngine.UIElements;

/// <summary>
/// Wires the UI Toolkit dropdown to ScreenSelection.
/// Attach to the same GameObject as your UIDocument component (ScreenSelectionUI).
/// Set the UIDocument's Source Asset to ScreenSelectionPanel.uxml.
/// Drag your kitchenView GameObject (with ScreenSelection attached) into the
/// Controller field in the Inspector.
/// </summary>
public class ScreenSelectionUI : MonoBehaviour
{
    [Tooltip("The GameObject with ScreenSelection attached")]
    public ScreenSelection controller;

    private DropdownField _dropdown;

    void OnEnable()
    {
        var root = GetComponent<UIDocument>().rootVisualElement;
        _dropdown = root.Q<DropdownField>("screen-type-dropdown");

        if (_dropdown == null || controller == null)
            return;

        // Initialise dropdown to match the controller's current screenType
        _dropdown.index = (int)controller.screenType;

        _dropdown.RegisterValueChangedCallback(evt =>
        {
            int index = _dropdown.choices.IndexOf(evt.newValue);
            controller.SetScreenType(index);
        });
    }
}
