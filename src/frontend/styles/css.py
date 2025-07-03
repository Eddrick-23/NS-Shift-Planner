custom_css = '''
<style>
.ag-cell {
    border-right: 0.5px solid #ddd !important;
    border-bottom: 0.5px solid #ddd !important;
    transition: all 0.2s ease !important;
}
.ag-cell:hover {
    border: 2px solid #2196f3 !important;   
}
.center-header {
    text-align: center !important;
    justify-content: center !important;
    display: flex !important;
    align-items: center !important;
}
.ag-header-group-cell-label {
    justify-content: center !important;
    display: flex !important;
    align-items: center;
    text-align: center;
    width: 100%;
}

@keyframes bounce-once {
  0%   { transform: scale(1); }
  30%  { transform: scale(1.01) translateY(-1px); }
  60%  { transform: scale(0.99) translateY(1px); }
  100% { transform: scale(1) translateY(0); }
}

.bounce-hover:hover {
  animation: bounce-once 0.4s ease;
}
</style>
'''
